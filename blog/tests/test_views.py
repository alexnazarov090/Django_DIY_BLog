from django.test import TestCase
from django.urls import reverse
from blog.models import BlogPost, BlogAuthor, Comment, User


class BlogListViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        blogger = BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')

        number_of_blogposts = 9

        for blog_id in range(number_of_blogposts):
            BlogPost.objects.create(title=f'Blog {blog_id}', description=f'This is the blog post #{blog_id}!', author=blogger)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/blogs/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blogpost_list.html')

    def test_pagination_is_five(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['blogpost_list']), 5)
    
    def test_lists_all_blogposts(self):
        # Get second page and confirm it has (exactly) remaining 4 items
        response = self.client.get(reverse('blog:blogs') +'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['blogpost_list']), 4)


class IndexViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK')
        test_user3 = User.objects.create_user(username='testuser3', password='1X<ISRUkw+tuK')
        test_user4 = User.objects.create_user(username='testuser4', password='1X<ISRUkw+tuK')
        test_user5 = User.objects.create_user(username='testuser5', password='1X<ISRUkw+tuK')
        test_user6 = User.objects.create_user(username='testuser6', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2.save()
        test_user3.save()
        test_user4.save()
        test_user5.save()
        test_user6.save()

        blogger1 = BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')
        blogger2 = BlogAuthor.objects.create(username=test_user2, bio='Hi! My name is test_user2!')
        blogger3 = BlogAuthor.objects.create(username=test_user3, bio='Hi! My name is test_user3!')
        blogger4 = BlogAuthor.objects.create(username=test_user4, bio='Hi! My name is test_user4!')
        blogger5 = BlogAuthor.objects.create(username=test_user5, bio='Hi! My name is test_user5!')
        blogger6 = BlogAuthor.objects.create(username=test_user6, bio='Hi! My name is test_user6!')

        number_of_blogposts = 20
        for blog_id in range(number_of_blogposts):
            if blog_id <= 10:
                BlogPost.objects.create(title=f'Blog {blog_id}', description=f'This is the blog post #{blog_id}!', author=blogger1)
            elif 10 < blog_id <= 15:
                BlogPost.objects.create(title=f'Blog {blog_id}', description=f'This is the blog post #{blog_id}!', author=blogger2)
            else:
                BlogPost.objects.create(title=f'Blog {blog_id}', description=f'This is the blog post #{blog_id}!', author=blogger3)

        BlogPost.objects.create(title='Blog 17', description='This is the blog post #17!', author=blogger4)
        BlogPost.objects.create(title='Blog 18', description='This is the blog post #18!', author=blogger5)
        BlogPost.objects.create(title='Blog 19', description='This is the blog post #19!', author=blogger6)

        number_of_comments = 8
        for comment_id in range(number_of_comments):
            if comment_id <= 2:
                Comment.objects.create(description=f'This is a comment {comment_id}!', blog=BlogPost.objects.get(pk=1), commenter=test_user2)
            else:
                Comment.objects.create(description=f'This is a comment {comment_id}!', blog=BlogPost.objects.get(pk=2), commenter=test_user3)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/index.html')

    def test_num_of_blog_posts(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        total_num = response.context['num_of_blog_posts']
        self.assertEqual(total_num, 23)

    def test_num_of_bloggers(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        total_num = response.context['num_of_bloggers']
        self.assertEqual(total_num, 6)

    def test_num_of_comments(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        total_num = response.context['num_of_comments']
        self.assertEqual(total_num, 8)

    def test_num_of_top_contributors_less_or_equal_then_five(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        top_contrs_dict = response.context['top_contributors']
        self.assertLessEqual(len(top_contrs_dict), 5)

    def test_top_contributors(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        top_contrs_dict = response.context['top_contributors']
        self.assertEqual(top_contrs_dict, {BlogAuthor.objects.get(pk=1): 11,
                                            BlogAuthor.objects.get(pk=2): 5,
                                            BlogAuthor.objects.get(pk=3): 4,
                                            BlogAuthor.objects.get(pk=4): 1,
                                            BlogAuthor.objects.get(pk=5): 1,})


class CommentCreateViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        blogger = BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')

        self.blog = BlogPost.objects.create(title='Blog 1', description='This is the blog post #1!', author=blogger)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('blog:comment-create', kwargs={'slug': self.blog.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('blog:comment-create', kwargs={'slug': self.blog.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_form.html')
    
    def test_redirects_to_blog_detail_view_on_success(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('blog:comment-create', kwargs={'slug': self.blog.slug}),
                                    {'description': 'This is the comment #1!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('blog:blog-detail', kwargs={'slug': self.blog.slug})))
