from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher, CourseChapter


class CourseModelCategorySerializer(ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ('id', 'name')


class CourseTeacherModelSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('name', 'title', 'id', 'signature')


class CourseListModelSerializer(ModelSerializer):
    teacher = CourseTeacherModelSerializer()

    class Meta:
        model = Course
        fields = ('id', 'name', 'lessons', 'course_img', 'students', 'pub_lessons', 'price', 'teacher', 'lesson_list')


class CourseInfoTeacherModelSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('name', 'title', 'id', 'signature', 'brief', 'image')


class CourseInfoModelSerializer(ModelSerializer):
    teacher = CourseInfoTeacherModelSerializer()

    # level = serializers.SerializerMethodField()

    # def get_level(self, obj):
    #     print(obj)
    #     return obj.get_level_display()

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'lessons', 'course_img', 'students', 'pub_lessons', 'price', 'teacher', 'get_level', 'brief_html',
            'course_video')


class CourseChapterModelSerializer(ModelSerializer):
    class Meta:
        model = CourseChapter
        fields = ['chapter', 'name', 'lesson_list']
