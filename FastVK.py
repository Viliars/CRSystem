import vk_api
from User import login1,password1,login2,password2


class FastVk():
	def __init__(self,a):
		self.vks = []
		self.i = -1
		self.len = len(a)
		for login,password in a:
			vk_session = vk_api.VkApi(login=login,password=password)
			try:
				vk_session.auth(reauth=True)
			except vk_api.AuthError as error_msg:
				print(error_msg)
			vk = vk_session.get_api()
			self.vks.append(vk)
	def __call__(self):
		self.i += 1
		return self.vks[self.i % self.len]

		

if __name__ == '__main__':
	vk = FastVk([(login1,password1),(login2,password2)])
	for i in range(4):
		vk().messages.send(user_id=116761932, message="Test Fast Vk " + str(i))
	
	
	
