from rest_framework import serializers
from .models import Bus, Route, BusStop, BusStudent, TransportAttendance


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStop
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class BusStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStudent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        bus = data.get('bus') or getattr(self.instance, 'bus', None)
        student = data.get('student') or getattr(self.instance, 'student', None)

        # Existing check: bus capacity se zyada students na hon
        current_count = BusStudent.objects.filter(bus=bus).exclude(
            id=getattr(self.instance, 'id', None)
        ).count()
        if current_count >= bus.capacity:
            raise serializers.ValidationError(f"Bus {bus.bus_no} is at full capacity ({bus.capacity}).")

        # NEW: ek student sirf ek hi bus mein assigned ho sakta hai (duplicate prevention)
        duplicate = BusStudent.objects.filter(student=student).exclude(
            id=getattr(self.instance, 'id', None)
        )
        if duplicate.exists():
            raise serializers.ValidationError(
                f"{student} is already assigned to a bus. Remove the existing assignment before adding a new one."
            )

        return data
class TransportAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportAttendance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
