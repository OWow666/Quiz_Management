from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    QUESTION_TYPES = [
        ('判断题', '判断题'),
        ('单选题', '单选题'),
    ]

    number = models.IntegerField(unique=True, verbose_name="题号")
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, verbose_name="题目类型")
    content = models.TextField(verbose_name="题干")
    options = models.JSONField(default=list, blank=True, verbose_name="选项")
    answer = models.CharField(max_length=255, verbose_name="答案")
    correct_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "题目"
        verbose_name_plural = "题库"

    def __str__(self):
        return f"题号: {self.number}, 类型: {self.type}"

class UserQuestionAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    shown_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    is_correct = models.BooleanField()
    attempt_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = "用户答题记录"
        verbose_name_plural = "用户答题记录"

    def __str__(self):
        return f"{self.user.username} - {self.question.number} ({'正确' if self.is_correct else '错误'})"


class WrongQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="题目")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "错误题"
        verbose_name_plural = "错误题记录"

    def __str__(self):
        return f"用户: {self.user.username}, 题号: {self.question.number}"