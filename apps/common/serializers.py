from rest_framework import serializers


class TenantModelSerializer(serializers.ModelSerializer):
    """Prevents a client from selecting a tenant and validates tenant relations."""

    def validate(self, attrs):
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            raise serializers.ValidationError("A valid tenant is required.")

        for value in attrs.values():
            if hasattr(value, "school_id") and value.school_id != tenant.id:
                raise serializers.ValidationError("Related records must belong to the current school.")
        return super().validate(attrs)
