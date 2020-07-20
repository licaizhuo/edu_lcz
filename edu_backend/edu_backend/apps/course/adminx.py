import xadmin
from course.models import *


class CourseCategoryModelAdmin(object):
    """课程分类表"""
    pass


xadmin.site.register(CourseCategory, CourseCategoryModelAdmin)


class CourseModelAdmin(object):
    """课程信息表"""
    pass


xadmin.site.register(Course, CourseModelAdmin)


class CourseChapterModelAdmin(object):
    """课程章节表"""
    pass


xadmin.site.register(CourseChapter, CourseChapterModelAdmin)


class CourseLessonModelAdmin(object):
    """课程课时表"""
    pass


xadmin.site.register(CourseLesson, CourseLessonModelAdmin)


class TeacherLessonModelAdmin(object):
    """讲师表"""
    pass


xadmin.site.register(Teacher, TeacherLessonModelAdmin)


class CourseDiscountTypeModelAdmin(object):
    """课程优惠类型"""
    pass


xadmin.site.register(CourseDiscountType, CourseDiscountTypeModelAdmin)


class CourseDiscountModelAdmin(object):
    """课程优惠折扣模型（价格优惠公式）"""
    pass


xadmin.site.register(CourseDiscount, CourseDiscountModelAdmin)


class ActivityModelAdmin(object):
    """优惠活动"""
    pass


xadmin.site.register(Activity, ActivityModelAdmin)


class CoursePriceDiscountModelAdmin(object):
    """课程与优惠策略的关系"""
    pass


xadmin.site.register(CoursePriceDiscount, CoursePriceDiscountModelAdmin)


class CourseExpireModelAdmin(object):
    """课程有效期模型"""
    pass


xadmin.site.register(CourseExpire, CourseExpireModelAdmin)
