from rest_framework import serializers

from core.models import Book, Publisher, Review


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'website', 'email']
        read_only_fields = ['id']

    # def create(self, validated_data):
    #     user = self.context.get('request').user
    #     publisher, created = Publisher.objects.get_or_create(user=user, **validated_data)
    #
    #     return publisher

    def update(self, instance, validated_data):
        publisher = super().update(instance, validated_data)

        return publisher


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'title', 'content', 'rating']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    publishers = PublisherSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_date', 'isbn', 'publishers']
        read_only_fields = ['id']

    def _get_or_create_publisher(self, book, publishers):

        user = self.context.get('request').user
        for publisher in publishers:
            publisher_obj, created = \
                Publisher.objects.get_or_create(user=user, **publisher)
            book.publishers.add(publisher_obj)

    def create(self, validated_data):

        publishers = validated_data.pop('publishers', [])
        book = Book.objects.create(**validated_data)
        self._get_or_create_publisher(book, publishers)

        return book

    def update(self, instance, validated_data):

        publishers = validated_data.pop('publishers', None)

        if publishers is not None:
            instance.publishers.clear()
            self._get_or_create_publisher(instance, publishers)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class BookSerializerOnlyView(BookSerializer):
    reviews = ReviewSerializer(many=True, required=False)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['reviews']
