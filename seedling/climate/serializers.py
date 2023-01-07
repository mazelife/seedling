from django.core.serializers.json import Serializer


class ClimateReadingSerializer(Serializer):

    def get_dump_object(self, obj):
        dict_repr = super(ClimateReadingSerializer, self).get_dump_object(obj)
        dict_repr["fields"]["degrees_fahrenheit"] = obj.degrees_fahrenheit
        return dict_repr["fields"]
