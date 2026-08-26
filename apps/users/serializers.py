from rest_framework import serializers
from .models import User, Student, Teacher, Staff, Parent


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student'),
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
        extra_kwargs = {'password': {'write_only': True}}


# Fields hidden unless the requesting tenant has the matching feature enabled.
# Key: serializer field name -> Value: feature key in the Feature registry.
FEATURE_GATED_FIELDS = {
    'blood_group': 'student-blood-group',
}


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Feature gating: drop fields the current school has not purchased.
        # The DB column still exists (shared schema) — only API visibility
        # changes, so no migration is needed to toggle a field per school.
        request = self.context.get('request')
        tenant = getattr(request, 'tenant', None)
        for field_name, feature_key in FEATURE_GATED_FIELDS.items():
            if tenant is None or not tenant.has_feature(feature_key):
                self.fields.pop(field_name, None)

    def validate(self, data):
        class_obj = data.get('class_obj') or getattr(self.instance, 'class_obj', None)
        if class_obj:
            current_count = Student.objects.filter(class_obj=class_obj).exclude(
                id=getattr(self.instance, 'id', None)
            ).count()
            total_capacity = sum(s.capacity for s in class_obj.sections.all())
            if total_capacity and current_count >= total_capacity:
                raise serializers.ValidationError(
                    f"Class '{class_obj.name}' has reached its total section capacity ({total_capacity})."
                )
        return data

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
