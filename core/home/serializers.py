from rest_framework import serializers
from .models import Person, Color
from django.contrib.auth.models import User

#! Refer this neat ModelSerializer
class RegisterSerializer(serializers.ModelSerializer):
    # username = serializers.CharField()
    # email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken...")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already taken...")
        return value

    #! Here we are using create_user rather than just create, so it takes care of password hashing. We do not have to do it manually.
    # when you call serializer.save(), it will trigger the create method of your RegisterSerializer to create the new user instance.
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user



# class RegisterSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     # def validate(self, data):
#     #     if data["username"]:
#     #         if (User.objects.filter(username=data["username"])).exists():
#     #             raise serializers.ValidationError("Username is already taken")

#     #     if data["email"]:
#     #         if (User.objects.filter(email=data["email"])).exists():
#     #             raise serializers.ValidationError("Email is already taken")

#     #     return data
#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise serializers.ValidationError("Username is already taken")
#         return value

#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email is already taken")
#         return value

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data["username"],
#             email=validated_data["email"]
#             # password=validated_data["password"],
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         # return validated_data
#         print(validated_data)
#         print(user)
#         print(user.password)
#         return user
        


#! If you want to make CUSTOM serializers using your own custom login, use serializers.Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["color_name"]
        # fields = ["color_name", "id"]


class PeopleSerializer(serializers.ModelSerializer):
    #! To know which model to serialize, we need Meta
    #! Meta needs 2 parameters, model to know which model to look upon and fields to know which columns/fields to serialize.
    # If you want serialize all fields, type "__all__"
    # If you want serialize only one fields i.e name, type "name", this will set required fields to only "name"
    #! Whichever field you are interested in, put it inside fields

    color = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), required=False
    )
    # color = ColorSerializer()  # by doing this, rather than just giving the f.k of color, it will give the data corresponding to that f.k
    color_info = (
        serializers.SerializerMethodField()
    )  # agar data ke saath alag ek parameter bhi dena hai jo ki model defination mein nahi hai

    class Meta:
        model = Person
        # fields = ["name", "age"]
        fields = "__all__"
        # fields = ["name"]
        depth = 1  # this will give data of foreign key rather than just foreign key. It is recommended not to use this method but to make a new serializer for foriegn key

    def get_color_info(self, obj):
        color = obj.color  # Get the color field
        if color is not None:
            color_obj = Color.objects.get(id=color.id)
            return {"color_name": color_obj.color_name, "hex_code": "#000"}
        else:
            return None  # Handle the case where color is None

    # def get_color_info(self, obj):
    #     color_obj = Color.objects.get(id=obj.color.id)  # fields = ["color_name", "id"] hai so id dikha nahi rahe but color table ka bhi id hai
    #     # return "India"
    #     return {"color_name": color_obj.color_name, "hex_code": "#000"}

    #! validate() is a method you can define within your serializer to perform custom validation logic beyond the standard field-level validations.
    def validate(self, data):
        special_characters = "!@#$%^&*()_+<>?/="
        if any(c in special_characters for c in data["name"]):
            raise serializers.ValidationError("Name cannot contain special chars...")

        if data.get("age") and data["age"] < 18:
            raise serializers.ValidationError("Age should be greater than 18...")
        return data
