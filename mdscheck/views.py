import os
import random
from decimal import Decimal

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Count, Q, OuterRef, Subquery, Prefetch, F, Exists, FloatField, ExpressionWrapper, \
    DecimalField, Func
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views import View
from django.db.models import Case, When
from .forms import EmailForm, PatternCheck, SearchForm
from .models import Images, MdsModel, Decision


class IndexView(View):

    def get(self, request):
        decisions = Decision.objects.filter(is_expert=False).order_by('-posted_date').select_related('image__case')[:15]
        context = {'decisions': decisions}
        return render(request, template_name='mdscheck/index.html', context=context)


class EmailEnterView(View):
    def get(self, request):

        try:  # Проверка на наличие значений почты и опыта в словаре request.session
            email = request.session['email']
            experience = request.session['experience']
            form = EmailForm(
                initial={'email': email, 'experience': experience, 'prev_url': request.META.get('HTTP_REFERER')})
        except KeyError:  # Если значения удалили или их нет, то выдает пустую форму
            form = EmailForm(initial={"experience": 'nov', 'prev_url': request.META.get('HTTP_REFERER')})

        context = {
            'form': form
        }
        return render(request, template_name='mdscheck/emailform.html', context=context)

    def post(self, request):
        posted_form = EmailForm(request.POST)
        if posted_form.is_valid():
            data = posted_form.cleaned_data
            request.session['email'] = data['email']
            request.session['experience'] = data['experience']
            return HttpResponseRedirect(reverse("mds_check:random_mds_case"))
        else:
            return render(request, template_name='mdscheck/emailform.html', context={'form': posted_form})


class EmailChangeView(View):
    # Вью для формы ввода почты
    def get(self, request):

        try:  # Проверка на наличие значений почты и опыта в словаре request.session
            email = request.session['email']
            experience = request.session['experience']
            form = EmailForm(initial={'email': email,
                                      'experience': experience,
                                      'prev_url': request.META.get('HTTP_REFERER')}
                             )
        except KeyError:  # Если значения удалили или их нет, то выдает пустую форму
            form = EmailForm(initial={"experience": 'nov', 'prev_url': request.META.get('HTTP_REFERER')})

        context = {
            'form': form
        }
        return render(request, template_name='mdscheck/emailform.html', context=context)

    def post(self, request):
        posted_form = EmailForm(request.POST)
        if posted_form.is_valid():
            data = posted_form.cleaned_data
            request.session['email'] = data['email']
            request.session['experience'] = data['experience']
            return HttpResponseRedirect(data['prev_url'])
        else:
            return render(request, template_name='mdscheck/emailform.html', context={'form': posted_form})


def logoutview(request):
    try:
        del request.session['email']
        del request.session['experience']
    except KeyError:
        print('Key error')
    return redirect(reverse('mds_check:index'))


class RandomMdsCaseView(View):
    template_name = 'mdscheck/mdscase.html'

    def get(self, request):
        if not request.session.get('email'):
            return redirect(reverse('mds_check:email_form'))
        cases = MdsModel.objects.all().annotate(decisions_count=Count('images__decisions')).order_by('decisions_count')
        random_case = random.choice(cases[:10])
        images = Images.objects.filter(case=random_case)

        form = PatternCheck(initial={'case_id': random_case.id})

        # номер файла - он в начале названия pdf файла, до '-'
        file_number = os.path.basename(random_case.pdf_file.name).split('-')[0]

        # 5 случайных доноров - для показа в карусели
        random_donors = random.sample(set(cases.filter(is_donor=True)), 5)

        if not str(request.META.get('HTTP_REFERER')).endswith(reverse('mds_check:random_mds_case')):
            request.session['count'] = 1

        if request.session['count'] > 10:
            request.session['count'] -= 1


        context = {
            'form': form,
            'cd13_cd11b': images[0],
            'cd13_cd16': images[1],
            'cd11b_cd16': images[2],
            'number': file_number,
            'random_donors': random_donors
        }

        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        if not request.session.get('email'):
            return redirect(reverse('mds_check:email_form'))

        form = PatternCheck(request.POST)
        if form.is_valid():
            valid_data = form.cleaned_data
            # получение QuerySet картинок по номеру кейса из формы
            images = Images.objects.filter(case_id=valid_data['case_id'])
            # заполнение каждого из трёх объектов Decision по отдельности
            # все, что можно вынести в повторяющееся - вынесено в цикл
            decisions = []
            decision_cd13cd11b = Decision()
            decision_cd13cd11b.decision = valid_data['is_normal_cd13cd11b']
            decision_cd13cd11b.image = get_object_or_404(images, name='1')
            decisions.append(decision_cd13cd11b)

            decision_cd13cd16 = Decision()
            decision_cd13cd16.decision = valid_data['is_normal_cd13cd16']
            decision_cd13cd16.image = get_object_or_404(images, name='2')
            decisions.append(decision_cd13cd16)

            decision_cd11bcd16 = Decision()
            decision_cd11bcd16.decision = valid_data['is_normal_cd11bcd16']
            decision_cd11bcd16.image = get_object_or_404(images, name='3')
            decisions.append(decision_cd11bcd16)

            for decision in decisions:
                decision.is_expert = False
                decision.responder = request.session['experience']
                decision.responder_email = request.session['email']
                decision.save()

        try:
            if request.session['count'] % 10 == 0:
                request.session['count'] += 1
                return redirect(reverse('mds_check:continue'))

            request.session['count'] += 1

        except KeyError:
            pass

        return redirect(reverse('mds_check:random_mds_case'))


class SearchView(View):
    template = 'mdscheck/casesearch.html'

    def get(self, request):
        search_form = SearchForm(initial={'case_number': 1})
        return render(request, template_name=self.template, context={'search_form': search_form})

    def post(self, request):
        search_form = SearchForm(request.POST)
        context = dict()
        if search_form.is_valid():
            number = search_form.cleaned_data['case_number']
            try:

                case = MdsModel.objects.get(number=number)
                return redirect(reverse('mds_check:mds_case', kwargs={'case_number': int(case.number)}))
            except (MdsModel.DoesNotExist, MdsModel.MultipleObjectsReturned):
                cases = MdsModel.objects.all().order_by('number')
                context = {'cases': cases}

        context['search_form'] = search_form
        return render(request, template_name=self.template, context=context)


def aboutview(request):
    return render(request, template_name='mdscheck/about.html')


def continueview(request):
    return render(request, template_name="mdscheck/continue.html")


class MdsCaseView(View):
    case_template_name = 'mdscheck/single_case.html'
    no_case_template_name = 'mdscheck/no_case.html'

    def get(self, request, case_number):
        try:
            case = MdsModel.objects.get(number=case_number)
            qs = Decision.objects.order_by('-is_expert')
            images = case.images.prefetch_related(Prefetch('decisions', queryset=qs)).select_related('case')
            context = {'case': case, 'images': images}
            return render(request, template_name=self.case_template_name, context=context)
        except (MdsModel.MultipleObjectsReturned, MdsModel.DoesNotExist):
            return render(request, template_name=self.no_case_template_name, context={'number': case_number})


def list_of_decisions(email, number=None):
    decisions = Decision.objects.select_related('image','image__case').all()
    if number == 0:
        decisions = decisions.filter(is_expert=False, responder_email=email).order_by('-posted_date')[:3]
    elif number:
        decisions = decisions.filter(is_expert=False, responder_email=email).order_by('-posted_date')[:number]
    else:
        decisions = decisions.filter(is_expert=False, responder_email=email).order_by('-posted_date')

    total_decisions = len(decisions)
    right_decisions = 0
    decisions_list = list()
    case_number = ""
    """
    создание сложного списка со словарями для передачи в темплэйт
    [{'case': MdsModel, 'decisions':[{'decision': Decision, 'expert_decision': Decision}, {}, {}]}, {}, ]
    """
    for decision in decisions:
        mds_case = decision.image.case
        mds_case_number = mds_case.number
        if mds_case_number != case_number:
            elem = dict()
            decisions_list.append(elem)
            elem['case'] = mds_case
            case_number = mds_case_number
            elem['decisions'] = list()
        try:
            expert_decision = Decision.objects.get(is_expert=True, image_id=decision.image_id)
            if expert_decision.decision == decision.decision:
                right_decisions += 1
            elem['decisions'].append({'decision': decision, 'expert_decision': expert_decision})
        except (Decision.MultipleObjectsReturned, Decision.DoesNotExist):
            if decision.decision == 'neg':
                right_decisions += 1
            elem['decisions'].append({'decision': decision, 'expert_decision': None})

    percent = 0
    try:
        percent = 100 * right_decisions / total_decisions
    except ZeroDivisionError:
        pass

    context = {'decision_list': decisions_list, 'total': total_decisions, 'right_decisions': right_decisions,
               'percent': percent}

    return context


class AnswersView(View):
    template_name = 'mdscheck/answers.html'

    def get(self, request):
        try:
            email = request.session['email']
        except KeyError:
            return redirect(reverse('mds_check:email_form'))

        context = list_of_decisions(email)

        paginator = Paginator(context['decision_list'], 10)
        page = request.GET.get('page')
        try:
            page_decisions = paginator.page(page)
        except PageNotAnInteger:
            page_decisions = paginator.page(1)
        except EmptyPage:
            page_decisions = paginator.page(paginator.num_pages)

        context['decision_list'] = page_decisions
        context['page'] = page
        return render(request, template_name=self.template_name, context=context)


class LastAnswersView(View):
    template_name = 'mdscheck/answers.html'

    def get(self, request):
        try:
            email = request.session['email']
        except KeyError:
            return redirect(reverse('mds_check:email_form'))

        context = list_of_decisions(email, number=(int(request.session.get('count'))-1)*3)

        return render(request, template_name=self.template_name, context=context)



class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 1)"


class StatisticsView(View):

    template = 'mdscheck/statistics.html'
    def get(self, request):
        expert_decisions = Decision.objects.filter(image=OuterRef('pk'), is_expert=True)
        images = Images.objects.annotate(
            right=Case(When(condition=Exists(expert_decisions.values('decision')), then=Count('decisions',
                        filter=Q(decisions__is_expert=False) & Q(decisions__decision=Subquery(expert_decisions.values('decision'))))),
                       default=Count('decisions', filter=Q(decisions__is_expert=False) & Q(decisions__decision='neg'))),
            tot=Count('decisions', filter=Q(decisions__is_expert=False)),
            percent=Case(When(tot=0, then=float('0')), default=Round(ExpressionWrapper(F('right') * Decimal('100.0')/F('tot'), output_field=FloatField(max_length=4))))
        )
        cases = MdsModel.objects.all().order_by('number').prefetch_related(Prefetch('images', queryset=images, to_attr='images_with_decisions'))


        paginator = Paginator(cases, 10)
        page = request.GET.get('page')
        try:
            page_cases = paginator.page(page)
        except PageNotAnInteger:
            page_cases = paginator.page(1)
        except EmptyPage:
            page_cases = paginator.page(paginator.num_pages)

        context = {
                    'cases': page_cases,
                    'page': page
                }

        return render(request, template_name=self.template, context=context)


