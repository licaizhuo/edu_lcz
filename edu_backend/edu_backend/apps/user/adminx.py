import xadmin

from user.models import UserCourse


class UserCourseModelAdmin(object):
    pass


xadmin.site.register(UserCourse, UserCourseModelAdmin)
