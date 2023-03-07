"""自定义分页组件，使用注意：
1.筛选数据
queryset = models.MobileLevelManage.objects.all()
2.实例化分页对象
page_object = Pagination(request,queryset)

context = {
        "queryset": page_object.page_queryset,   # 分完页的数据
        "page_string": page_object.html()     # 页码
    }
return render(request,"moblie_list.html",context)

"""
from django.utils.safestring import mark_safe
import copy


class Pagination(object):
    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 请求的对象
        :param queryset: 符合条件的数据（根据这个数据进行分页处理）
        :param page_size:每页显示多少条数据
        :param page_param:在URL中传递的获取分页的参数，例如：/etty/list?page=12
        :param plus:显示当前页的前或后几页
        """
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size
        self.page_start = (page - 1) * page_size
        self.page_end = page * page_size
        self.page_queryset = queryset[self.page_start:self.page_end]
        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count
        self.plus = plus

    def html(self):
        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:

                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        # 页码
        page_str_list = []
        self.query_dict.setlist(self.page_param, [1])
        # print(self.query_dict.urlencode())
        page_str_list.append(
            '<li class="page-item"><a class="page-link" href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))
        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            prev = '<li class="page-item"><a class="page-link" href="?{}">上一页</a></li>'.format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            prev = '<li class="page-item"><a class="page-link" href="?{}">上一页</a></li>'.format(
                self.query_dict.urlencode())
        page_str_list.append(prev)

        # 页面
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                # self.query_dict.setlist(self.page_param, [i])
                ele = '<li class="page-item active"><a class="page-link" href="?{}">{}</a></li>'.format(
                    self.query_dict.urlencode(), i)
            else:

                ele = '<li class="page-item"><a class="page-link" href="?{}">{}</a></li>'.format(
                    self.query_dict.urlencode(), i)
            page_str_list.append(ele)

            # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            prev = '<li class="page-item"><a class="page-link" href="?{}">下一页</a></li>'.format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.total_page_count])
            prev = '<li class="page-item"><a class="page-link" href="?{}">下一页</a></li>'.format(
                self.query_dict.urlencode())
        page_str_list.append(prev)
        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append(
            '<li class="page-item"><a class="page-link" href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))
        page_string = mark_safe("".join(page_str_list))
        return page_string
