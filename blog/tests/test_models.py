from django.test import TestCase
from blog.models import BlogPost, BlogAuthor, Comment, User
from datetime import date


class BlogPostTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        blogger = BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')
        BlogPost.objects.create(title='Test1', post_date=date.today(), description='This is the test of blog post!', author=blogger)
    
    def test_title_label(self):
        blogpost = BlogPost.objects.get(id=1)
        field_label = blogpost._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')
    
    def test_title_max_length(self):
        blogpost = BlogPost.objects.get(id=1)
        max_length = blogpost._meta.get_field('title').max_length
        self.assertEqual(max_length, 100)

    def test_description_label(self):
        blogpost = BlogPost.objects.get(id=1)
        field_label = blogpost._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_post_date_label(self):
        blogpost = BlogPost.objects.get(id=1)
        field_label = blogpost._meta.get_field('post_date').verbose_name
        self.assertEqual(field_label, 'post date')
    
    def test_author_label(self):
        blogpost = BlogPost.objects.get(id=1)
        field_label = blogpost._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_get_absolute_url(self):
        blogpost = BlogPost.objects.get(id=1)
        self.assertEqual(blogpost.get_absolute_url(), f'/blog/blog/{date.today()}-test1')

    def test_expected_object_name(self):
        blogpost = BlogPost.objects.get(id=1)
        expected_object_name  = f'{blogpost.title}'
        self.assertEqual(str(blogpost), expected_object_name)


class BlogAuthorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')
    
    def test_username_label(self):
        blogger = BlogAuthor.objects.get(id=1)
        field_label = blogger._meta.get_field('username').verbose_name
        self.assertEqual(field_label, 'username')

    def test_bio_label(self):
        blogger = BlogAuthor.objects.get(id=1)
        field_label = blogger._meta.get_field('bio').verbose_name
        self.assertEqual(field_label, 'bio')

    def test_bio_max_length(self):
        blogger = BlogAuthor.objects.get(id=1)
        max_length = blogger._meta.get_field('bio').max_length
        self.assertEqual(max_length, 1000)

    def test_get_absolute_url(self):
        blogger = BlogAuthor.objects.get(id=1)
        self.assertEqual(blogger.get_absolute_url(), '/blog/blogger/1')

    def test_expected_object_name(self):
        blogger = BlogAuthor.objects.get(id=1)
        expected_object_name  = f'{blogger.username}'
        self.assertEqual(str(blogger), expected_object_name)


class CommentTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2.save()

        blogger = BlogAuthor.objects.create(username=test_user1, bio='Hi! My name is test_user1!')
        blogpost = BlogPost.objects.create(title='Test1', description='This is the test of blog post!', author=blogger)
        Comment.objects.create(description='This is a comment!', blog=blogpost, commenter=test_user2)
        Comment.objects.create(description='This is a looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong comment!',
                                blog=blogpost,
                                commenter=test_user2)
        

    def test_post_date_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('post_date').verbose_name
        self.assertEqual(field_label, 'post date')

    def test_description_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_description_max_length(self):
        comment = Comment.objects.get(id=1)
        max_length = comment._meta.get_field('description').max_length
        self.assertEqual(max_length, 1000)
    
    def test_blog_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('blog').verbose_name
        self.assertEqual(field_label, 'blog')

    def test_commenter_label(self):
        comment = Comment.objects.get(id=1)
        field_label = comment._meta.get_field('commenter').verbose_name
        self.assertEqual(field_label, 'commenter')

    def test_expected_object_name(self):
        comment = Comment.objects.get(id=1)
        expected_object_name  = f'{comment.description}'
        self.assertEqual(str(comment), expected_object_name)
    
    def test_expected_object_name_less_or_equal_75(self):
        long_comment = Comment.objects.get(id=2)
        self.assertEqual(len(str(long_comment)), 75)
