from rest_framework.decorators import api_view
from rest_framework.response import Response

from home.models import Person, Color
from home.serializers import PeopleSerializer, LoginSerializer, RegisterSerializer

from rest_framework.views import APIView
from rest_framework import viewsets, status

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.paginator import Paginator


class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        print(serializer.data)
        #! authenticate defination => If the given credentials are valid, return a User object.
        user = authenticate(
            username=serializer.data["username"], password=serializer.data["password"]
        )

        if not user:
            return Response(
                {"status": False, "message": "Invalid Credentials, user not found..."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        print("Token => ", token)
        return Response(
            {
                "status": True,
                "message": "User login successfully...",
                "Token": str(token),
            },
            status=status.HTTP_201_CREATED,
        )


class RegisterAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # when you call serializer.save(), it will trigger the create method of your RegisterSerializer to create the new user instance.
        serializer.save()
        return Response(
            {"status": True, "message": "User created successfully..."},
            status=status.HTTP_201_CREATED,
        )


class PersonAPI(APIView):
    #! Now if the user is not authenticated, data will not be accessable.
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            print(request.user)
            # objs = Person.objects.filter(color__isnull=False)
            objs = Person.objects.all()
            #! here we are using paginator
            page = request.GET.get("page", 1)
            page_size = 3
            paginator = Paginator(objs, page_size)
            print(paginator.page(page))

            serializer = PeopleSerializer(paginator.page(page), many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"status": False, "message": "Invalid Page..."})

    def post(self, request):
        data = request.data
        serializer = PeopleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request):
        data = request.data
        serializer = PeopleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def patch(self, request):
        data = request.data
        obj = Person.objects.get(id=data["id"])
        serializer = PeopleSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request):
        data = request.data
        obj = Person.objects.get(id=data["id"])
        obj.delete()
        return Response({"message": "Person data deleted..."})


class PeopleViewSet(viewsets.ModelViewSet):
    serializer_class = PeopleSerializer
    queryset = Person.objects.all()

    #! Here we overwrote the existing list() with our list() which includes search functionality.
    def list(self, request):
        search = request.GET.get("search")
        queryset = self.queryset

        if search:
            queryset = queryset.filter(name__startswith=search)

        serializer = PeopleSerializer(queryset, many=True)
        return Response(
            {"status": 200, "data": serializer.data}, status=status.HTTP_204_NO_CONTENT
        )


# @api_view(['GET','POST','PUT'])
# def index(request):
#     courses = {
#         'course_name':'Python',
#         'learn':['flask', 'django', 'tornado', 'fastAPI'],
#         'course_provider': 'SCALAR'
#     }
#     if request.method == 'GET':
#         #! To get search or filter parameter in URL. Only applicable on GET requests
#         print(request.GET.get('search'))
#         print("You hit a GET method...")
#         return Response(courses)
#     elif request.method == 'POST':
#         print("You hit a POST method")
#         #! To get data passed by user during POST request
#         data = request.data
#         print("*******************************************")
#         print(data)
#         print(data["name"])
#         print("*******************************************")
#         return Response(courses)
#     elif request.method == 'PUT':
#         print("You hit a PUT method")
#         return Response(courses)


@api_view(["GET", "POST"])
def index(request):
    courses = {
        "course_name": "Python",
        "learn": ["flask", "django", "tornado", "fastAPI"],
        "course_provider": "SCALAR",
    }
    if request.method == "GET":
        json_response = {
            "name": "SCALAR",
            "courses": ["C++", "Python"],
            "method": "GET",
        }
    else:
        data = request.data
        print(data)
        json_response = {
            "name": "SCALAR",
            "courses": ["C++", "Python"],
            "method": "POST",
        }
    return Response(json_response)


@api_view(["POST"])
def login(request):
    data = request.data
    serializer = LoginSerializer(data=data)

    if serializer.is_valid():
        data = serializer.validated_data
        print(data)
        return Response({"message": "Success..."})

    return Response(serializer.errors)


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def person(request):
    if request.method == "GET":
        # objs = Person.objects.all()
        objs = Person.objects.filter(color__isnull=False)
        # objs will be a queryset returning ['1','2'.....'n']
        #! If size of queryset is more than 1, pass "many=True" into the serializer
        serializer = PeopleSerializer(objs, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = request.data
        serializer = PeopleSerializer(data=data)
        #! serializer.is_valid() checks whether the data recieved follows the rules imposed like all the reqd fields and datatype, etc.
        #! When you call is_valid(), the serializer runs all the built-in and custom validation rules defined in the serializer class, such as field validations, unique constraints, and any custom validators you've added.
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == "PUT":
        data = request.data
        serializer = PeopleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == "PATCH":
        # In Django REST framework (DRF), a serializer for the PATCH method typically requires two parameters: instance(obj) and data
        data = request.data
        obj = Person.objects.get(id=data["id"])
        serializer = PeopleSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    else:
        data = request.data
        obj = Person.objects.get(id=data["id"])
        obj.delete()
        return Response({"message": "Person data deleted..."})
