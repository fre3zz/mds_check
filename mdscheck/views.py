import os
import random

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views import View

from .forms import EmailForm, PatternCheck, SearchForm
from .models import Images, MdsModel, Decision


class IndexView(View):
    # Вью для главной страницы, она статичная, поэтому ничего в контекст не передаем
    def get(self, request):
        return render(request, template_name='mdscheck/index.html')


class EmailEnterView(View):
    # Вью для формы ввода почты
    def get(self, request):

        try:  # Проверка на наличие значений почты и опыта в словаре request.session
            email = request.session['email']
            experience = request.session['experience']
            form = EmailForm(initial={'email': email, 'experience': experience})
        except KeyError:  # Если значения удалили или их нет, то выдает пустую форму
            form = EmailForm(initial={"experience": 'nov'})
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
        return redirect(reverse('mds_check:index'))


def logoutview(request):
    try:
        del request.session['email']
        del request.session['experience']
    except KeyError:
        print('Key error')
    return render(request, template_name='mdscheck/logout.html')


class RandomMdsCaseView(View):
    template_name = 'mdscheck/mdscase.html'

    def get(self, request):
        if not request.session.get('email'):
            return redirect(reverse('mds_check:email_form'))
        cases = MdsModel.objects.all()
        random_case = random.choice(cases)
        images = Images.objects.filter(case=random_case)

        form = PatternCheck(initial={'case_id': random_case.id, })

        # номер файла - он в начале названия pdf файла, до '-'
        file_number = os.path.basename(random_case.pdf_file.name).split('-')[0]

        # 5 случайных доноров - для показа в карусели
        random_donors = random.sample(set(cases.filter(is_donor=True)), 3)

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
                print(number)
                case = MdsModel.objects.get(number=number)
                return redirect(reverse('mds_check:mds_case', kwargs={'case_pk': int(case.id)}))
            except MdsModel.DoesNotExist:
                context = {'cases': MdsModel.objects.order_by()}
        context['search_form'] = search_form
        return render(request, template_name=self.template, context=context)




class MdsCaseView(View):
    def get(self, request, case_pk):
        return HttpResponse("!!!")