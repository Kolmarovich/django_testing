from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Comment

BAD_WORDS = (
    'редиска',
    'негодяй',
    # Дополните список на своё усмотрение.
)
WARNING = 'Не ругайтесь!'


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        """Не позволяем ругаться в комментариях."""
        text = self.cleaned_data['text']
        lowered_text = text.lower()
        if any(word in lowered_text for word in BAD_WORDS):
            raise ValidationError(WARNING)
        return text
