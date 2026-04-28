from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_friend_requests_user_friends_user_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='avatars/',
                verbose_name='Аватарка',
                validators=[users.models.validate_image_extension],
            ),
        ),
    ]
