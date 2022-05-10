# from rest_framework.generics import ListAPIView, CreateAPIView
# from django.shortcuts import render
# from youtube.models import VideoInfo
# from .serializers import GetSingleVideoInfo



# class VideosList(ListAPIView):
#     serializer_class = GetSingleVideoInfo
#     def get_queryset(self):
#         email = self.kwargs['email']
#         return VideoInfo.objects.filter(user__email=self.kwargs['email'])


# class GetVideosInfoAPI(CreateAPIView):
#     serializer_class = GetSingleVideoInfo
#     def 