from crispy_forms.bootstrap import Alert
from django.core.mail.backends import console
from django.core.serializers import serialize
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST

from .forms import UserRegisterForm
from .models import Question, WrongQuestion, UserQuestionAttempt
import json
from django.shortcuts import render, redirect
from django.db.models import Count, Q, F
import random

def index(request):
    return render(request, 'index.html')


def get_questions(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        if request.user.is_authenticated:
            seen_questions = UserQuestionAttempt.objects.filter(
                user=request.user
            ).values_list('question_id', flat=True)
            questions = questions.exclude(id__in=seen_questions)

        return JsonResponse({
        'questions': [{
            'fields': {
                'id': q.id,
                'content': q.content,
                'type': q.type,
                'options': q.options,
                'answer': q.answer
            }
        } for q in questions]
    })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def get_wrong_questions(request):
    if request.method == 'GET' and request.user.is_authenticated:
        wrong_questions = UserQuestionAttempt.objects.filter(
            user=request.user,
            correct_count__lt=3,  # Need 3 correct answers to remove
            is_correct = False
        ).distinct()

        question_num = [wq.question.number for wq in list(wrong_questions)]

        wrong_questions_real = Question.objects.filter(
            number__in=question_num
        )

        return JsonResponse({
            'questions': [{
                'fields': {
                    'id': r.id,
                    'content': r.content,
                    'type': r.type,
                    'options': r.options,
                    'answer': r.answer
                }
            } for r in wrong_questions_real]
        })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@csrf_exempt
def save_wrong_question(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    try:
        data = json.loads(request.body)
        # question_id = data.get('question_id')

        question = Question.objects.get(id=data['question_id'])
        WrongQuestion.objects.get_or_create(
            user=request.user,
            question=question
        )
        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Question.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def clear_user_data(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                UserQuestionAttempt.objects.filter(user=request.user).delete()
                WrongQuestion.objects.filter(user=request.user).delete()
            return JsonResponse({'status': 'success', 'message': '所有题目进度已重置'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=400)

@require_POST
@csrf_exempt
def record_attempt(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')

        if not question_id or is_correct is None:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)

        question = Question.objects.get(id=question_id)

        if question not in [UQA.question for UQA in list(UserQuestionAttempt.objects.filter(user=request.user,question=question))]:
            UserQuestionAttempt.objects.create(
                user=request.user,
                question=question,
                is_correct=is_correct
            )
            UserQuestionAttempt.objects.filter(
                user=request.user,
                question=question
            ).update(correct_count=F('correct_count') + 1)
            return JsonResponse({'status': 'success'})

        # Remove from wrong questions if reached 3 correct attempts
        if is_correct:
            UserQuestionAttempt.objects.filter(
                user=request.user,
                question=question
            ).update(correct_count=F('correct_count') + 1)
            correct_attempts = UserQuestionAttempt.objects.filter(
                user=request.user,
                question=question
            ).first()
            if correct_attempts.correct_count >= 3:
                WrongQuestion.objects.filter(
                    user=request.user,
                    question=question
                ).delete()

        return JsonResponse({'status': 'success'})
    except Question.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
        else:
            print(form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')