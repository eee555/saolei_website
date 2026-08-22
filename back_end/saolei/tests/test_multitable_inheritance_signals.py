from django.db import connection, models
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.test import TransactionTestCase


class SignalParent(models.Model):
    parent_field = models.CharField(max_length=20, default='')

    class Meta:
        app_label = 'common'


class SignalChild(SignalParent):
    child_field = models.CharField(max_length=20, default='')

    class Meta:
        app_label = 'common'


class MultiTableInheritanceSignalTests(TransactionTestCase):
    available_apps = ['common']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(SignalParent)
            schema_editor.create_model(SignalChild)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(SignalChild)
            schema_editor.delete_model(SignalParent)
        super().tearDownClass()

    def setUp(self):
        self.events = []
        self.receivers = []
        for signal_name, signal in [
            ('pre_save', pre_save),
            ('post_save', post_save),
            ('pre_delete', pre_delete),
            ('post_delete', post_delete),
        ]:
            for sender in [SignalParent, SignalChild]:
                receiver = self.make_receiver(signal_name)
                signal.connect(receiver, sender=sender, weak=False)
                self.receivers.append((signal, receiver, sender))

    def tearDown(self):
        for signal, receiver, sender in self.receivers:
            signal.disconnect(receiver, sender=sender)

    def make_receiver(self, signal_name):
        def receiver(sender, instance, **kwargs):
            event = {
                'signal': signal_name,
                'sender': sender.__name__,
                'pk_exists': instance.pk is not None,
            }
            if signal_name == 'post_save':
                event['created'] = kwargs['created']
            if 'update_fields' in kwargs:
                update_fields = kwargs['update_fields']
                event['update_fields'] = None if update_fields is None else set(update_fields)
            self.events.append(event)
        return receiver

    def assert_events(self, expected):
        self.assertEqual(self.events, expected)

    def test_create_child_instance_signal_order(self):
        SignalChild.objects.create(parent_field='parent', child_field='child')

        self.assert_events([
            {'signal': 'pre_save', 'sender': 'SignalChild', 'pk_exists': False, 'update_fields': None},
            {'signal': 'post_save', 'sender': 'SignalChild', 'pk_exists': True, 'created': True, 'update_fields': None},
        ])

    def test_save_child_instance_with_child_only_update_fields(self):
        child = SignalChild.objects.create(parent_field='parent', child_field='child')
        self.events.clear()

        child.child_field = 'child-updated'
        child.save(update_fields=['child_field'])

        self.assert_events([
            {'signal': 'pre_save', 'sender': 'SignalChild', 'pk_exists': True, 'update_fields': {'child_field'}},
            {'signal': 'post_save', 'sender': 'SignalChild', 'pk_exists': True, 'created': False, 'update_fields': {'child_field'}},
        ])

    def test_save_child_instance_with_parent_only_update_fields(self):
        child = SignalChild.objects.create(parent_field='parent', child_field='child')
        self.events.clear()

        child.parent_field = 'parent-updated'
        child.save(update_fields=['parent_field'])

        self.assert_events([
            {'signal': 'pre_save', 'sender': 'SignalChild', 'pk_exists': True, 'update_fields': {'parent_field'}},
            {'signal': 'post_save', 'sender': 'SignalChild', 'pk_exists': True, 'created': False, 'update_fields': {'parent_field'}},
        ])

    def test_delete_child_instance_signal_order(self):
        child = SignalChild.objects.create(parent_field='parent', child_field='child')
        self.events.clear()

        child.delete()

        self.assert_events([
            {'signal': 'pre_delete', 'sender': 'SignalChild', 'pk_exists': True},
            {'signal': 'pre_delete', 'sender': 'SignalParent', 'pk_exists': True},
            {'signal': 'post_delete', 'sender': 'SignalChild', 'pk_exists': True},
            {'signal': 'post_delete', 'sender': 'SignalParent', 'pk_exists': True},
        ])

    def test_delete_parent_instance_signal_order(self):
        child = SignalChild.objects.create(parent_field='parent', child_field='child')
        parent = SignalParent.objects.get(pk=child.pk)
        self.events.clear()

        parent.delete()

        self.assert_events([
            {'signal': 'pre_delete', 'sender': 'SignalChild', 'pk_exists': True},
            {'signal': 'pre_delete', 'sender': 'SignalParent', 'pk_exists': True},
            {'signal': 'post_delete', 'sender': 'SignalChild', 'pk_exists': True},
            {'signal': 'post_delete', 'sender': 'SignalParent', 'pk_exists': True},
        ])
