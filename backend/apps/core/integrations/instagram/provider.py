"""Official integration contract. This MVP cannot send Instagram messages."""
from abc import ABC,abstractmethod
from dataclasses import dataclass
@dataclass(frozen=True)
class MessageRequest:
 recipient_id:str
 text:str
 conversation_id:str
class InstagramProvider(ABC):
 @abstractmethod
 def send(self,request:MessageRequest)->str:raise NotImplementedError
class DisabledInstagramProvider(InstagramProvider):
 def send(self,request:MessageRequest)->str:
  raise RuntimeError('Instagram not connected: official Meta OAuth and permissions required')
class MockInstagramProvider(InstagramProvider):
 """Only use for explicit local tests, never for production delivery."""
 def send(self,request:MessageRequest)->str:
  from django.conf import settings
  if not settings.DEBUG:raise RuntimeError('Mock provider requires local development mode')
  return 'mock:'+request.conversation_id
