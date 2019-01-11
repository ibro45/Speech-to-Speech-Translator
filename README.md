# The Babel Fish - Speech-to-Speech Translator

The Babel Fish v0.01 took inspiration from the same-named fish from the novel *The Hitchhiker's Guide to the Galaxy*. 

It is defined as:
>The Babel fish is a small, bright yellow fish, which can be placed in someone's ear in order for them to be able to hear any language translated into their first language. 

How this translator achieves something that reminds of it is by using a neural network to identify the
language that a speaker is talking (Croatian, French and Spanish supported). 
Once it has recognised the language, that information is passed on
to several Google APIs in order to produce the English translation of it and to return it
as synthesised speech. 

Here you can see the video of the application in action
VIDEO

The application is also available online. The live demo can be found at LINK


## Technical details
The neural network was created and trained using Tensorflow. The code can be found can be found at LINK

The project's backend is written in Flask. As mentioned, Google APIs are used for speech recognition (Speech-to-Text LINK), text translation (Translate LINK) and speech synthesis (Text-to-Speech LINK).

This project requires Tensorflow since the model was built using it. If you'd like to install a GPU version, which is not necessary
for the project, check out LINK. Otherwise, just install it using requirements.txt where the CPU version is specified along other dependencies.

Furthermore, FFmpeg and SoX should be installed manually.

