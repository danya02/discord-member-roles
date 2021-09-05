import peewee as pw

db = pw.SqliteDatabase('/config.db')

class MyModel(pw.Model):
    class Meta:
        database = db

class RoleChannel(MyModel):
    guild = pw.IntegerField()
    channel = pw.IntegerField()
    role_prefix = pw.CharField()
    role_suffix = pw.CharField()
    vote_emoji = pw.CharField()
    default_color = pw.IntegerField()

    class Meta:
        indexes = (
                (('guild', 'channel'), True),
                )

class ReactionRole(MyModel):
    channel = pw.ForeignKeyField(RoleChannel)
    message_id = pw.IntegerField(index=True)
    role_id = pw.IntegerField(index=True)

db.create_tables([RoleChannel, ReactionRole])
