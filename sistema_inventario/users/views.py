from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required


def signup(request):
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Cuenta creada correctamente. Ahora puedes iniciar sesión.')
			return redirect('login')
		else:
			# Collect form errors and show as message
			error_list = []
			for field, errors in form.errors.items():
				for err in errors:
					error_list.append(f"{field}: {err}")
			if error_list:
				messages.error(request, 'Errores en el formulario: ' + ' | '.join(error_list))
	else:
		form = UserRegistrationForm()
	return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
	# Simple profile view showing user information
	return render(request, 'users/profile.html', {'user': request.user})
