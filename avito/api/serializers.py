from rest_framework import serializers

from main.models import Bb, Comment

class BbSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Bb для нескольких записей.'''
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at')


class BbDetailSerializaer(serializers.ModelSerializer):
    '''Сериализатор модели Bb для определенной записи.'''
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price',
                  'created_at', 'contacts', 'image')
        

class CommentSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Comment.'''
    class Meta:
        model = Comment
        fields = ('bb', 'author', 'content', 'created_at')

