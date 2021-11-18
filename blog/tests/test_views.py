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
