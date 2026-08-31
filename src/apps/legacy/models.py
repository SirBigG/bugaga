from django.db import models


class Category(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(null=True)
    lft = models.IntegerField()
    rgt = models.IntegerField()
    level = models.IntegerField()
    tree_id = models.IntegerField(null=True)
    parent = models.ForeignKey(
        "self",
        db_column="parent_id",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="children",
    )

    class Meta:
        managed = False
        db_table = "category"

    def __str__(self):
        return self.title


class TelegramUser(models.Model):
    date_joined = models.DateTimeField(null=True)
    telegram_key = models.CharField(max_length=255, null=True)
    temp_key = models.CharField(max_length=255, null=True)
    is_subscribed = models.BooleanField(null=True)
    is_admin = models.BooleanField(null=True)
    categories = models.ManyToManyField(
        Category,
        through="UserCategoryAssociation",
        related_name="telegram_users",
    )

    class Meta:
        managed = False
        db_table = "tusers"

    def __str__(self):
        return self.telegram_key or str(self.pk)


class UserCategoryAssociation(models.Model):
    pk = models.CompositePrimaryKey("telegram_user", "category")
    telegram_user = models.ForeignKey(
        TelegramUser,
        db_column="user_id",
        on_delete=models.DO_NOTHING,
        related_name="category_associations",
    )
    category = models.ForeignKey(
        Category,
        db_column="category_id",
        on_delete=models.DO_NOTHING,
        related_name="telegram_user_associations",
    )

    class Meta:
        managed = False
        db_table = "user_category_association"

    def __str__(self):
        return f"{self.telegram_user_id}:{self.category_id}"


class ParserMap(models.Model):
    category = models.ForeignKey(
        Category,
        db_column="category_id",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="parser_maps",
    )
    host = models.CharField(max_length=255)
    link = models.TextField()
    map = models.TextField()
    root = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField()
    last_crawling = models.DateTimeField(null=True, blank=True)
    period = models.IntegerField()
    period_type = models.CharField(max_length=25)
    is_active = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "parsermap"

    def __str__(self):
        return self.link


class ParsedItem(models.Model):
    data = models.TextField()
    hash = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        db_column="category_id",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="parsed_items",
    )
    created = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "parseditem"

    def __str__(self):
        return self.hash


class AdvertParserMap(models.Model):
    host = models.CharField(max_length=255)
    link = models.TextField()
    map = models.TextField()
    root = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField()
    content_type = models.IntegerField()
    is_active = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "advertparsemap"

    def __str__(self):
        return self.host


class Link(models.Model):
    link = models.TextField()
    is_parsed = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "link"

    def __str__(self):
        return self.link


class Advert(models.Model):
    data = models.TextField()
    link = models.TextField()
    hash = models.CharField(max_length=500, null=True)
    category = models.IntegerField(null=True)
    location = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    created = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "advert"

    def __str__(self):
        return self.link


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.TextField(null=True)
    created = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "news"

    def __str__(self):
        return self.title
