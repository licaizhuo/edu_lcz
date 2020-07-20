from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher, CourseChapter


class CourseModelCategorySerializer(ModelSerializer):
    """获取所有课程分类的序列化器"""

    class Meta:
        model = CourseCategory
        fields = ('id', 'name')


class CourseTeacherModelSerializer(ModelSerializer):
    """在CourseListModelSerializer中嵌套的序列化器，用来获取老师的信息"""

    class Meta:
        model = Teacher
        fields = ('name', 'title', 'id', 'signature')


class CourseListModelSerializer(ModelSerializer):
    """获取课程列表的序列化器"""
    # 自定义字段，嵌套序列化器
    teacher = CourseTeacherModelSerializer()

    class Meta:
        model = Course
        fields = ('id', 'name', 'lessons', 'course_img', 'students', 'pub_lessons', 'price', 'teacher', 'lesson_list',
                  'discount_name', 'real_price')


class CourseInfoTeacherModelSerializer(ModelSerializer):
    """在CourseInfoModelSerializer中嵌套的序列化器，用来获取老师的信息"""

    class Meta:
        model = Teacher
        fields = ('name', 'title', 'id', 'signature', 'brief', 'image')


class CourseInfoModelSerializer(ModelSerializer):
    """获取某个课程的详细的信息的序列化器"""
    # 自定义字段，嵌套序列化器
    teacher = CourseInfoTeacherModelSerializer()

    # level = serializers.SerializerMethodField()

    # def get_level(self, obj):
    #     print(obj)
    #     return obj.get_level_display()

    class Meta:
        model = Course

        # brief_html:将课程详细的介绍中的符合条件的src进行替换
        # discount_name : 优惠活动的名称
        # active_time:剩余活动的时间
        # comment_length：评论的数目
        fields = (
            'id', 'name', 'lessons', 'course_img', 'students', 'pub_lessons', 'price', 'teacher', 'get_level',
            'brief_html', 'course_video', 'discount_name', 'real_price', 'active_time', 'comment_length')


class CourseChapterModelSerializer(ModelSerializer):
    # 获取章节的信息的序列化器
    class Meta:
        model = CourseChapter
        # lesson_list 在model的Course类中，自定义了一个函数属性。用来获取每个章节对应的课时信息
        fields = ['chapter', 'name', 'lesson_list']
