from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Room(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    username = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    message_content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)

    class Meta:
        ordering = ('date_added',)

    def __str__(self):
        return f"{self.username}: {self.message_content[:30]}"


class MessageRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user}"


class DirectMessageRoom(models.Model):
    user1 = models.ForeignKey(User, related_name='dm_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='dm_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def clean(self):
        # Ensure consistent user order to avoid duplicate rooms
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DM Room: {self.user1.username} ↔ {self.user2.username}"

    @classmethod
    def get_or_create_room(cls, user_a, user_b):
        user1, user2 = sorted([user_a, user_b], key=lambda u: u.id)
        room, created = cls.objects.get_or_create(user1=user1, user2=user2)
        return room


class DirectMessage(models.Model):
    room = models.ForeignKey(DirectMessageRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_content = models.TextField()
    file = models.FileField(upload_to='uploads/dm/', null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender.username}: {self.message_content[:30]}"


class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, related_name='blocked_users', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"
