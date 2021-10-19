textFile = f"Hello! username-here" \
           f"\nHere is the code for your verification: code-here" \
           f"\nOr! you can go to this link here: link-here" \
           f"\nPlease don't respond to this email."

htmlFile = """\
<html>
	<body style="margin: 0;padding: 0;box-sizing: border-box;height: 100%;width: 100%;padding-top: 50px;padding-left: 150px;background-color: gray;">
		<div style="margin:0;box-sizing:border-box;border: 2px solid black;border-radius: 25px;background-color: white;width: 500px;height: 550px;padding: 10px 20px;">
			<header style="margin: 0;padding: 0;box-sizing: border-box;border: 2px solid gray;text-align: center;margin-bottom: 50px;">
				<h1>Hello! username-here</h1>
			</header>
			<article style="border: 2px solid gray;height: 300px;padding: 10px 20px;">
				<p style="text-align: center;">
				Here is your code for verification!: 
				</p>
				<p style="color: green;text-align: center;font-size: 25px;">
				code-here
				</p>
				<p style="text-align: center;">
				Or! You could go to this link! 
				</p>
				<p style="text-align: center;font-size: 25px;">
				<a href="link-here">
				Click me!
				</a>
				</p>
				<p style="background: gray;border: 2px solid black;padding: 5px;">
				Do note: After your email verification, the admin will be able to activate your account. But you will not be able to access it until so.
				</p>
			</article>
			<footer style="margin: 0;padding: 0;box-sizing: border-box;">
				<p style="margin: 0;padding: 0;box-sizing: border-box;">
					This was sent by an account that may or may not be moderated. As it's main purpose is only to send this email, Please don't reply or email back. Thank you!
				</p>
			</footer>
		</div>
	</body>
</html>
"""