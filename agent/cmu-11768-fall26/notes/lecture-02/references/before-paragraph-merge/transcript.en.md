# CMU 11-768 Fall 2026 · Lecture 2 · Agent Capabilities 1: Tool Use

- 视频：[官方视频](https://www.youtube.com/watch?v=jXChFB4JSyw&list=PLSN0qpDfUvTM&index=2)
- 字幕：en-orig · auto captions
- 处理：连续字幕合并为自然段；每段保留首条字幕的起始时间戳
- 状态：原语言字幕稿，待校对

---

## 正文

[00:00.640] Okay. So, hi everyone. Uh, welcome to class number two. Today, uh, today I'll be talking about tool use for language model agents. And, uh, this is, you know, the the most fundamental thing about agents that, uh, you know, makes them different from a language model.

[00:23.279] Um so the basic idea here is uh that we're going to be um a tool is basically an interface through which a language model can invoke an external computer program. And uh this is a language model cannot do this on its own because it's fundamentally a token predicting machine. But this enables you to do you know many many different things. So you know you can search, you can call a

[00:50.000] calculator, you can call a browser, um you can call Python, you can call arbitrary APIs and so uh the language model kind of as you'll see the method for tool calling is standardized but what you do downstream with the tool call can be very different. So there's basically two uh benefits of tools and all of this is from one of the readings that I I posted on the website

[01:17.119] if you want to go back and read more about it. Uh this is a survey that uh I we wrote uh together Daniel and I and Zoro Wong, one of our our students. Um and the first thing is extending the ability of language models. So this is giving language models the ability to do something that they fundamentally cannot do. And so this could be like accessing

[01:40.079] information or actions that are outside the language model's um you know action space. The second thing is uh facilitating the language model. And so what I mean by this is this is something that fundamentally the language model can do but it's just a lot easier if you don't if you don't require the language model to do it.

[02:02.479] So um can anybody come up with an example or well I guess we already have an example in here. So like one thing the the language model fundamentally cannot do would be get the time four months ago or something like that. So the most recent information it saw is uh from four months ago and then its parameters are frozen. So there's no way it could know that without calling you

[02:24.080] know an external function. On the other hand, uh something in the realm of facilitating is language models can do math actually quite well nowadays, but they take a lot longer than calling a calculator to do math because they have to do reasoning like you ask them to multiply uh two seven-digit numbers and it will take them a very long time to do

[02:45.120] it where a calculator can do that really quickly. So those are the two kind of basic categories. So um to go a little bit more deeply into those uh you can do things like look up current information um and the benefit of this is this gives you you know fresh evidence to uh ground your answers uh do exact computation using like calculators or python this gives

[03:09.920] you the ability to execute more reliably or and quickly than using the language model itself. Um other things is uh access private states. So giving the model access to like information about the user so they can uh respond based on the user state um or uh make a change to your external environment. So this could be like browsing or or calling an API.

[03:33.280] So to have some examples of these um if we think about chat GPT uh chat GPT used to like literally just be text in and text out when it first came out. it, you know, the the only thing that it could do was give you textual responses to uh your queries. Now, it's kind of an everything app. It allows you to do so many different things. Um, so like what what are some of the

[04:00.560] examples of things that uh you know are your top use cases of uh of using chat GPD now? >> Yeah. >> Writing code. Okay. So uh what what tool would you need for something like that? uh like cursor or codeex I think they they can invoke like >> okay but that's not chat GPT right that's cursor or codeex yeah I mean chat GPT like in the chat GPT interface

[04:30.080] >> they can use blender so they they can render blender okay things so that that's an example of um something that requires executing code but also like displaying it in the appropriate format um any any other ones that people do yeah Just the web page generate images.

[04:49.919] >> Generate images. Yeah. So that that's calling an image generation tool. Any others? >> Yeah. So recommend products like a blender or something like this. And for this uh what what sort of tool do you think it would need? >> Some sort of like web searches like Google or Amazon to find.

[05:19.919] >> Yep. So you might need like arbitrary web search or you might need an API that directly links into Google or Amazon or something like that. Yeah. Any other like weirder weirder ones? Things you were surprised chat GPT was able to do? >> Yeah. >> You can render latex quite nicely.

[05:35.440] >> Okay. messed up files when I fix you the PDF >> and compile everything which is very handy sometimes. >> Yep. Ren, it can render latex. Well, I actually don't know if this is a tool or if this is just a front-end interface thing, but it might be just that it's rendered in your web browser.

[05:52.160] >> Oh, it creates a PDF. So, okay. Is a tool. Okay. Very cool. Yeah. >> Interact >> uh interact with like Slack or something like that. So, that's another specialized API. So all kinds of different things. Um I I kind of categorized these into a list of things that I think are um the most uh like typical tools and most of the other tools can kind of be categorized into

[06:17.360] each of these. So the first one is uh textual responses. So this is kind of the boring one where it just gives you an answer. Um there's two ways you can implement this within an agentic uh like loop. By the way, chat GPT is is an agent now. Uh if you're like if there was any question about it, chat GPD is not just a chat app. It's an agent because it makes uh iterative tool calls

[06:41.280] to answer your queries. So that's kind of the definition of an agent. Um but uh textual responses, there's two ways you can implement these. One way you can implement these is you can have a finish tool that says, "Okay, I'm done interacting with the user, so I'm just going to finish and and output some text." The other way you can do it is if the agent decides to not call a tool,

[07:02.319] you can just finish the agentic loop. So that's kind of uh you know the the simple u you know most obvious one. Another extremely common one. Um so all all of these are tools and so like theoretically all of them can be thought of as an API but uh just to break them down a little bit more. Um another one is searching the web and this is you know pulling in information um from all

[07:28.479] of these uh different settings. Um how many people have heard of retrieval augmented generation? Probably everybody everybody who took the NLP class here uh you know has heard of it but a lot of people. How many people have heard like rag is dead? [snorts and laughter] A fairly large number of people. So there there's been an argument in like language model

[07:50.880] circles that retrieval augmented generation was so like two years ago and like nobody cares about it anymore. My argument here is a retrieval augmented generation where you retrieve context and then generate answers based on it has become so normal that people don't even realize that they're using it anymore. And so um it's it's so alive that people think it's dead. Um but uh

[08:12.720] basically you know searching the web and retrieving information and then generating answers based on it is now essentially the norm uh within these uh these applications. Now so uh that's another tool that's provided very very broadly and like any chat uh interface.

[08:29.919] Another one is code execution and so this is uh throwing in uh you know a set of code to do uh calculations or or something like this. very useful for uh computation all the other stuff we talked about. Another common one is uh having some sort of image generation and uh this this is you know obviously another very popular use case in chat GPT. Um this one's a little bit

[08:56.320] different because like all of the other ones here uh that I was talking about basically you know mostly interface with text. Um here this is interfacing with uh this is interfacing with images. One interesting thing is uh you'll notice that this is not the same thing is here.

[09:16.640] So this is like water watercolor robot studying in a library where the query was actually different. And so a big part of calling these images is actually deciding what query to put in there. So the language model will like really really expand the query before it calls an image generation API. I don't know if you can see this anymore in chat GPT, but you used to be able to see in chat

[09:38.720] GPT when you downloaded the image um that it would have like a very different caption than the caption you gave and you could kind of like latently see what the uh what query the the image generator uh sent to the generate image tool. Then there's all all kinds of uh you know custom functions. So, um, like buy me buy me bananas, uh, milk and coffee.

[10:03.600] Um, so, you know, this could create a grocery cart, uh, for you and call the like Instacart API to do this. Um, and you can basically go as wild as you want with all these tools and and add whichever ones you want there. Okay, so there's a bunch of different ways you can think about tool calling.

[10:27.040] Um the first way you can think about tool calling is just you provide a list of uh 50 or 70 API functions that the agent is able to inter interact with and it can call these uh APIs and if you do that basically what you're doing is like every step you're calling one API or if you're doing parallel tool calling you're calling multiple APIs or something like this but code is kind of

[10:55.040] a special uh API uh because code is extremely uh you know expressive and you can view code as like a meta tool right so within this we have like the bakers baked 200 loaves of bread how many loaves of bread did they have left here this is calling an assignment tool an assignment tool this is calling a subtraction tool um this is calling a uh assignment tool you

[11:23.600] know etc etc so like essentially Um I I imagine that a lot of people have taken like a programming languages course or have some familiar familiarity with programming languages but basically you you can express each piece of code is a tree of these function calls um and these uh the tree can also be have loops and other uh control flow in it. So it's essentially

[11:49.920] you know a very rich way of calling uh tools. Um and so uh you can also pull in external libraries. So these are now the custom APIs that you pull into your uh pull into your system. So uh you know now if you're calling pandas now you've opened up all of the like tools in pandas right and um you know you can build your own utility functions. So you could call uh

[12:20.560] special purpose functions that you want uh as well. So code is kind of special. It's like one of the one of the you know special things that uh it's different from other tools in the way that it like opens up your ability to call tools in new ways. And so there's actually uh research work that demonstrates that this is very effective. Uh right now we basically

[12:44.079] take it for granted but this was not how uh not how we called tools like three or four years ago uh when we first started uh you know building agents with LLMs. And so the the standard then was like if you got a a query sorry this is very small but um it basically says determine the most cost-effective country to purchase the smartphone model Kodak 1.

[13:07.200] Uh the countries to consider are the US uh Japan, Germany and India. Basically, what this would require you to do was uh you would call your lookup rates tool on Germany. Um you would call your lookup phone price uh tool. You would call uh convert and tax. Then you would call lookup rates again. Then you would call uh look up phone price and you would

[13:30.160] step over and over and over again uh in order to uh finally get uh finally get the result. But if you write code, you can just write like a single program to perform this. And so uh this makes it like a much richer uh a much more efficient way of calling tools in addition to be being richer. And so this method called uh called Kodak has a paper uh about it and

[13:55.040] uh some of the core results from the paper are essentially the success rate goes up and the average number of interaction turns goes down. And this is even for tasks that didn't traditionally require code. These are for tasks that were like viewed as regular tool use tasks. Um but like code is just like a good medium uh for how you would do this.

[14:18.560] Um but there's a reason why people don't use code uh programmatic tool calling for everything. Um and it largely has to do with um with like the level of power that you want to give to the agent. So code is very highowered. So it's expressive. It gives you loop variables and libraries. This is good. But what could be a downside of this?

[14:41.040] Any ideas? Ju just with respect to loops variables uh loops and variables at first maybe. Yeah. >> Get stuck. >> Yeah, it could get stuck. So it could write an infinite loop and then you need to have something in your system to deal with infinite loops, right? That's uh that's a little bit annoying. Um what about libraries?

[15:01.199] any problem with that? >> Yeah, security problems would be one thing. Also, maybe just versioning and stuff like this, but um I'm not sure if people are familiar with this, but one of the major issues with agents in cyber security right now is the agents will pull in a library that has been compromised. Um the agent gets compromised and then your whole system

[15:21.680] gets compromised. So, uh this is something uh something you need to be very careful about. Um they're also uh harder con to constrain because they have the broad action space. So uh it's you know harder to validate and uh get predictable behavior. Um they also have higher impact. So they can you know use more disk uh sorry use more memory, use more

[15:43.120] disk, use more CPU and stuff like this. And so because of this um we'll talk about this more in the safety lecture, but like once you move to programmatic tool calling, you need to be uh you need to think about sandboxes and how you're going to contain the agent and stuff like that as well.

[15:59.600] Um any any questions about this? Cool. Okay. So I want to uh talk next about the mech uh mechanics of providing tools and right now uh every language model is basically pretty good at uh like calling tools but this was not you know taken for granted. I I think I mentioned this on Tuesday as well. Um but basically tool calls are um expressed as tokens like this. And so um you know a text

[16:35.680] continuation is the weather is sunny. A tool continuation is uh like a tool call and then you have get weather or something like this within the the tool call. And very often uh you have both in the same uh output. So if you remember react uh which was talked about before um I can actually draw this on the board but react basically you have your text up here

[17:08.240] and then you have your uh tool call and then you have your tool call down here. Yeah, this is like the end of the tool call. And so now you have the the model be being uh giving a response to the human uh while it's making the tool call. And then uh in here you have the like actual tool call that it's making. And so the react loop is no longer expressed as

[17:39.760] like separate code. It's expressed more as like just a single completion. um if you're using one of the reasoning models um that can reason uh like have long reasoning traces and stuff like that. In addition, you might have like the thinking tokens up here and then a message and then the tool calls. And so the thinking is like very verbose thinking that you don't show to the

[18:05.120] user. The text is the less verbose uh message that you show to the user and then the tool call is like the actual output you have there. Yeah, >> the tool call tokens has to be in the vocabulary of the model during pre-training also, right? >> Yes. >> So all of these service tokens are going to be vocabulary.

[18:26.799] >> Uh yes. So actually that's a good point. I said yes, but the answer might be no. I'm going to repeat the question first. So the question was um do these tokens have to be in the vocabulary when you do pre-training? Um, typically if you're pre-training on all of the internet, you don't necessarily have to have them in the vocabulary yet. Um we there are

[18:48.000] cases where you might do that but it's actually more typical to introduce them in a process of mid-training which is like uh between uh it's when you're training on like moderately large amounts of data on things in the format that you like and then uh you might do reinforcement learning after that but you might not necessarily have them when you pre-train on the whole internet.

[19:10.400] Cool. Um so I think this should likely be familiar to um you know uh people who have implemented things in uh previous natural language processing or or whatever courses. But um if you have the chat format like the open AAI chat format you have things like the system message, the user message, the assistant message and then uh these are represented as something like JSON in

[19:42.240] uh like in Python when you call the call the model but these get converted into something uh with like a special token here the system uh like this is a system prompt and then be concise and stuff like this. So like each chat message gets its own format and this is an example of the quen format but uh as I'll show later the other uh other functions are in different formats. So

[20:11.360] tools basically um add a structure to the request and so you have a tool definition like this and uh this tells you that it's a function. The function name might be get weather. Um the parameters are city and the type is a string and this is required. And this schema gets passed to for example the chat completions function that you you would use when calling openAI or

[20:39.440] something like this. So um when the prompt uh contains something like this, you might have uh this included in the tools section of the prompt and then the output uh ends up being something like name get weather uh with the appropriate arguments like the city of Pittsburgh.

[21:02.799] So um we we had a question about how you pre-train the models and um you might not be pre-training but at least at mid-training and beyond you will be training the model to fit a particular tool call format. The interesting thing is uh every model has a different tool call format. Maybe not everyone but many of the different ones. And so uh Quen has like im start tool call uh IM end.

[21:29.280] Uh Mistall has tool calls and then uh all of the tool calls. Deepseek has their like DSML DeepS markup language function calls. They they don't call it tool calls. they call it function calls and then evoke invoke and basically you know any of these works. Um there might be like minor minor differences in uh which one gets better performance or not if you train the same model with the

[21:52.240] same data. Uh but what you need to know is you need to know that these are different. So you can't just assume that like some parsing code that works with deepseek will suddenly work with quen and vice versa. Yeah. >> You said you add functionality. So need to provide.

[22:17.280] >> Um, so what do you mean by loose generalizability? >> Yep. fine tuning set of >> Yeah. So when you're when you're fine-tuning, you will want to match like if you're fine-tuning from a model that's already been trained, you 100% want to match the tool call format. You don't want to try to get it to do something it wasn't trained on. Um, and the good news is this is all

[22:57.280] implemented in like hugging face with the apply chat template uh function. And so you need to apply the chat template for the model you're using, but that's all implemented. If it's not implemented properly, you can go in and um like it you ask them and they'll go in and implement it or you do it yourself or something like that. But yeah, it's it's all standardized now. But I I want to

[23:20.799] people to know that this is going on under the hood because if you don't know this, you can make mistakes and uh and it will not be happy. Cool. So um once you have done this uh the next thing is um that you do tool call parsing and actually I'm going to talk about tool called kernel parsing in the next section. So um not immediately here but like let's assume

[23:47.919] that if uh the language model outputs this you have a way of parsing it into uh into the function arguments. you then um like have the you register the tool at initialization and um you uh have a way to resolve it so that you get a map from the name to the tool that you want to execute. So most agentic frameworks basically will will have a way that you

[24:15.919] can add new tools. Each tool gets its own name and then you have a Python function or something like that. Python, TypeScript, whatever language. And then it uh it will be dispatched to that with the appropriate arguments. And so then at each time you you parse uh you look up the tool, you validate the uh action from the arguments and you execute uh and then you return. But um at

[24:40.720] validation time, this can fail if the model gave you the wrong uh the wrong tool call. At execution time, this can also fail if there's like not something that was explicitly said is bad uh is like invalid but implicitly is invalid. So like for example, if you have an execute Python tool, it might accept any string as Python, but then when you actually try to run the Python, it it

[25:05.039] might fail. So that that would be like an execution error. And then if it does if it well whether it uh whether it fails or not, then uh you get an observation out of it. So this is another detail um that that's pretty helpful but also really annoying uh when you're implementing agents if you if you get it wrong. But basically each tool call is assigned an ID uh when

[25:33.279] you uh when you run it basically by um uh either the language model inference code or the agent code and then you get a result and the result has a matching call ID and this is useful especially in the case of parallel tool calling because I'm going to talk about parallel tool calling in a bit and having the IDs matched lets you know which tool call is

[25:57.840] associated assiated with with which result. But the uh the problem is uh for instance uh anthropic if you have a tool call with no matched tool result it will die on you and uh so it will tell you this is an invalid history and I'm not going to accept this history and and generate any more outputs for you. And so in my practical experience there's times when for example the assistant

[26:26.000] makes a tool call then suddenly uh your your program dies or something like that it fails to write out the tool result and then you resume it it doesn't have the result the associated result and uh anthropic fails to fails to work for you. So this is a little bit of a a detail that you need to know.

[26:47.120] Okay. So, um, any any questions there? Yeah. >> And, uh, great question. Are the tool calls asynchronous? Um, I'm going to talk about that in like the the next next section. Yeah. Cool. Okay. So, now now here's a very technically algorithmically difficult problem. Uh, that may be very interesting to you or maybe not not very interesting to you. But if it's not

[27:16.720] interesting to you, be glad that other people are solving it for you. Um, so, uh, language models are definitely not guaranteed to generate well-formed tool calls. Um, and this is an example. Uh, you can see that this is JSON that's missing the uh, last closing bracket.

[27:36.320] So, this is poorly formed JSON. You put this into your JSON parsing program and it will throw an exception and you won't be able to get the uh, the data out of it. So I I've seen a million people go in and try to like figure out if the brackets are missing and like add one post hawk, but you don't want to be doing that. That's not not fun. Um so there's a bunch of constraints uh that

[27:58.480] you uh could be assigning to each of the tool calls. So the first one is syntax. So it has to be valid JSON. So this is kind of like table stakes, right? So it it needs to parse. Um the second thing is uh shape. So make sure that if you have expected or required fields, you have the required fields. Um the third thing is types. So uh you know if you

[28:22.799] have city, the city must be a string. Oh sorry. Yeah. Um yeah. So if you have a city, city is a string. Um if you have uh values, uh you know the units are in the appropriate units. So this can all be expressed through um something called JSON schema or basically any schema library. Um so it's like this is a city uh the type is string and the units can

[28:48.640] be uh Celsius or Fahrenheit and city is required. So um the the good thing about this is this has machine readable validation rules. So you can check if like a call uh follows the schema. But um one way that you can express whether the schema is valid or invalid is by defining a grammar over uh over the schema. And how many people uh did like contextf free grammarss or like context

[29:22.159] or those sorts of things? Regular grammarss. How many people know regular expressions? Okay. A lot of a lot of people. Okay. So a regular expression is a regular grammar. Um does anybody know how you can parse a regular expression? >> Finite state automaton. Yeah, that's exactly correct. Um so a finite state automaton uh for for those who are less familiar with this is

[30:04.080] something that looks a little bit like this. Um, so you have a state and every time you take a token as input, uh, you move to a different state. So if you get A, you would move to this state. If you get B or C, you move to this state. And This this works on uh something called uh uh regular grammarss. So regular expressions like the the slashes and dot

[30:36.640] stars and stuff like this that you might use to search for search text are uh reg are regular expressions and they can be expressed through regular grammars. Um JSON schema cannot be expressed through a regular grammar. um it can be expressed through something called a contextf free grammar and you can uh the context free grammar can basically make a tree that looks a little bit like

[31:00.320] this. So um every JSON expression can have brackets on the side. It can have commas between its members. Uh this can be a string um and this can be a unit. And if uh the JSON schema is in the correct format, you should be able to create a tree uh that looks like this.

[31:21.120] If the JSON schema is in the wrong format, you might create a be able to create create most of a tree. But then when you get to a unit, a unit cannot be K. So basically this would uh this would fail even though a unit can be K, but uh we we defined this to not accept Kelvin as our our unit of temperature.

[31:42.320] So um basically if you can parse uh the tool call with a contextf free grammar uh defined from your JSON schema you can uh you can do this and I'm not going to go into a lot of details but a finite state automaton cannot parse a um a contextf free grammar but there's something called a push down automaton that can allow you to do this. So basically it adds a stack to uh the

[32:10.159] regular grammar and uh you push things onto the stack uh pop things off of the stack and eventually can um eventually can decide whether it's uh parsible or not. And so what you do is you start out at the very beginning um with uh a state in this push down automaton and you step through and uh validate your output as you um as you generate it from left to right

[32:38.399] and I'm giving some examples from X grammar uh and X grammar is a thing that's actually pretty widely used in uh all of the LM inference libraries. It's actually developed by people in the machine learning department here. Uh so what you uh what this means is every time you get an LLM predict the logits of the next token, you take a look at your grammar and if the grammar says

[33:05.679] this is a valid next token, uh you get a score of one and if you have an invalid next token, you get a score of zero. And you set all of the invalid next tokens to negative infinity. um for the output logits and then you renormalize so that you get probability only on the valid tokens. And so what this uh lets you do is this ensures that you generate valid output.

[33:31.919] Um, and so this is another figure from the Xgrammer paper and they do these uh tricky things where basically there are some vocabulary that are always valid or always invalid and you premputee these and then there what there are those that are valid only in some contexts only in some uh stack context and then you calculate them on the fly. So it's uh

[33:58.960] very interesting algorithmically if you like algorithmic uh stuff. If you don't like it uh be glad that the people in the machine learning department are doing it for you basically. Um so because of this almost always um if you are uh if you are have this enabled you will uh and set your appropriate JSON schema you will get wellformed to tool calls. So that that's uh that's great.

[34:27.040] There's one case where you actually can't uh uh get well-formed tool calls despite this. Um may maybe I can give a quick quiz. This is very very difficult. So I don't know if anybody can get it. But any anybody have an idea where even this would not be uh not be enough. Need to be familiar with uh with LMS I guess.

[34:50.399] >> Yeah. Uh I I think that's close enough to what I I wanted to say. So basically um when you run out of tokens, so models can only generate so many tokens and you might run into a place where you're still on a valid path through the automaton, but you're not at the final state. So you generate like part of a JSON output. So very very good. Um and I

[35:17.520] I've actually encountered this. There's uh theoretically a way you could do that which is like you count the number of output tokens that you still have left and you you cut them off but that's uh if if somebody wants to implement that in next grammar as a extra credit assignment you know be happy to happy to have that okay so now um let's go to rest API calling um so there's uh two

[35:44.880] different ways to um there's different ways to Express tools and um I'd say probably most people are familiar with REST APIs. The these are the ways you interact with web services. Um but actually sorry there's one other way to call APIs and one way to call APIs is through programmatic tool calling where basically um you just give the model a Python program and you say use the stuff

[36:12.320] in this Python program to call tools. And so if you do something like that you might have like weather lib.py pi and uh you have the get weather function in here uh with its city and its units and uh then you just say call this function whenever you need to and you give it the ability to execute Python and it will be able to call that tool. So in programmatic tool calling this uh this

[36:34.240] works but this is not um callable remotely and it's also not callable from the like standard method of tool calling that you use um that you use when you uh implement this uh not through non-programmatic tool calling. So there's a way to turn this into uh REST APIs. Has anybody used fast API before? It's a pretty common Okay. a lot of people. It's a pretty common library.

[37:02.880] And basically what this allows you to do is this allows you to create a web uh web backend uh extremely simply by just uh setting up a fast API uh giving an API key so you can get people to validate against the API and then writing a Python decorator where uh weather becomes uh becomes this. And so this is good uh for a couple reasons.

[37:29.520] The first reason is maybe if you don't want people uh looking at the weather um then uh you can prevent them from looking at the weather. But probably more importantly if you don't want people like getting your personal data or something like that you can require an API key and uh this will uh allow you to block anybody who doesn't have an appropriate API key for instance. Um the

[37:51.280] other reason why is this gives you a JSON schema for free. uh and when I say for free of course you know this is something that's implemented in in fast API but your entire API can be expressed as a JSON schema and that JSON schema can then be provided as is to a language model and that language model can then use it uh to you know specify which calls are allowed and so then you could

[38:13.680] go in and process this and um whenever the agent made a tool call you could then send it to your API server and they it could use that on the API server Um, another option for calling these is you can just uh use the curl command. And the curl command um basically allows you to call these APIs uh directly like this as well. And so if you have a a coding

[38:37.920] agent that has access to bash, it has the ability to um to call like this. So this is maybe maybe reasonably straightforward if you're familiar with uh REST and stuff like this. Any any questions or comments or If you haven't played around with fast API, it's nice. It's very easy to use.

[39:00.640] But um the reason why I wanted to cover this first is this is kind of like the traditional way of of programming uh you know before agents. Um there's uh something called MCP the model context protocol and this was introduced by anthropic uh maybe twoish years ago or a year and a half ago and the idea was this is was designed to be a standard way to uh give your model

[39:28.560] additional context. When I first saw this I actually was like why do we need to do this? I don't understand why we need to do this. Let's uh let's just let our uh agents call APIs. Um but there is one uh important point about one one or two important points that make MCP different from just calling a normal API. Uh and I'll I'll explain them here. But um first I'll

[39:56.000] explain why I didn't real I didn't like I thought this was not actually necessary. And basically the reason why is every time you set up an MCP, what you do is you have your AI application and then you set up a couple MCP clients. So like maybe this is your weather client uh your this is your weather MCP and your uh your GitHub MCP or something like that. So you can ask

[40:21.839] what the weather is what the weather is and push it to your GitHub. Um uh and the reason why I didn't think this was necessary originally was because like why do you need to run a program to call an API, right? We already have good ways to call APIs. We just, you know, send it to the the REST API server.

[40:43.920] But um okay. Yeah. So so that's a little bit of an aside. Um, uh, I'll I'll get back to that in a moment, but for a little bit of an aside, uh, there's a really nice library called fast MCP. And fast MCP is basically designed to be fast API for MCP. So if you want to create an MCP server for whatever you want, you can um, just like basically swap out fast

[41:08.800] MCP and swap it uh, swap out fast API and swap in fast MCP and you can uh, create an MCP server very easily. Um, you can also take in a spec that was generated by like a REST API and just turn it in into an MCP as well. But here here's the main reason why you might want to use MCP uh as opposed to an API. Uh, and the reason why is because it gives you an extra layer of

[41:38.319] security. And so MCPs have an MCP API key. And this MCP API key uh is something that you need to provide to the process that's running your agent. Separately from this, you have the upstream API key. So like let's say you are getting um getting your agent to connect to your GitHub. The upstream API key would be your GitHub token and you would provide that to the MCP server,

[42:05.599] but you would not provide it to the agent. And then what you provide to the agent is the MCP API key, which allows you to authenticate into the MCP server. And so the reason why this is important is what happens if you give your agent the GitHub your GitHub token and your agent suddenly decides that it's a good idea to push that to your public GitHub repository.

[42:28.480] Not good, right? [laughter] Your account gets compromised and uh you get malware installed onto all your repositories or something like this. So you want to give the the agent something that is relatively harmless. Uh so that even if it leaks it for whatever reason like that leak is relatively harmless and then the um the actual credentials get get preserved and so that was basically

[42:51.280] the reasoning behind it. So um just to go into a summary, they all give you the ability to add a set of APIs into uh into your agent. Like you could do that through a regular JSON schema or through an MCP. Um the uh but a lot of other things are different. So like for discovery um you might need to fetch an open API uh document. For MCP there is a special API

[43:19.680] that allows you to list all of the tools. Um for invocation um you call an HTTP uh thing here for um MCP there's an MCP transport and this can be through various ways. You connect through standard IO or you connect through an H uh uh a socket or something like that.

[43:39.599] Uh I already talked about authentication and um MCP actually has a few other um has a few other like conveniences like you can add resources, prompts and extensions, but I'm not going to go into a lot of detail about that. Cool. Um actually, um there's two other things I'd like to mention. um there I don't want to uh I I guess I forgot to add them to my slide. Um so the first thing

[44:11.040] is um MCP registry. There's an official MCP registry. So if you want to find MCPS uh that allow you to do something like this, you can, you know, go to this registry and find uh any of a very large number of MCPS. There's also like a million and a half uh MCP server like websites that you can go to that are are ranked based on uh popularity and stuff

[44:39.200] like this. Another thing is um I've been talking a lot about the Pittsburgh weather and uh the funny thing is uh today I prepared all of these slides like earlier of course but today we actually got Pittsburgh weather that was simultaneously rainy and sunny at the same time. And so I managed to break my own API because it cannot return multiple states at the same time. But uh

[45:03.280] uh yeah, it was uh quite the coincidence. You can see the torrential downpour and the the bright side at the same time. Okay. Uh back back to serious stuff. Cool. Um so another big uh kind of like development pretty recently is parallel tool calling. in parallel tool calling.

[45:25.200] Um the the basic problem we want to solve is the same problem that I talked about when I talked about like the codec and the programmatic tool calling which is if you call tools one at a time. Um the uh it it could become very long for even a simple operation because you might do a weather and then do a calendar and then do a flight. Um, but if tool calls are independent, you can

[45:49.920] actually call them at the same time. And this is done pretty simply. You just like add add multiple tool call blocks to a single agent response. The um there's a few nuances about this. The first one is um you can only paralyze tool calls if they don't have dependencies on each other. So, um, like if you were looking up the weather for Pittsburgh and reading today's calendar

[46:16.960] and looking up flight status, that might be, uh, might be good. Um, but if you need to find a customer ID, use it to fetch orders and refund the selected order. Obviously, you can't do that. So, there's limits to the parallel tool calling you could do. And if your calendar or your flight was dependent on the weather, then you know, obviously that'd be a problem, too.

[46:37.440] So, there was a question about this. Um, do you execute the tool calls in parallel? And the answer is typically yes. You can just uh use typical Python uh syntax to you know have a whole bunch of tool calls and then execute them and then uh use something like async.io.gather to uh to return the results of them when they run in the same time. So this is uh uh this is

[47:01.119] pretty common. Another thing I'd like to point out is um this is a major difference between really efficient language models in note efficient language models. And there there's this weird weird paradox in agentic language models nowadays that more expensive models more expensive models can actually be cheaper if you measure them on a taskbytask basis. And there's two major reasons for

[47:31.920] this. The first major reason is more expensive models can be smarter. So they pick like an appropriate solution more quickly. Um but another thing is um more recent models do parallel tool calling uh a lot better. So they make a whole bunch of calls at the same time. So if you're using a coding agent or something like this, uh you use the the better uh you

[47:57.359] use the better models and they are doing like a bunch of view images at the same time or they're uh like writing a bunch of different files at the same time or something like that. That's because they're doing parallel tool calling. Well, um does anyone have an idea of like why they got so much better at this? They like this was not a huge thing even though parallel tool calling

[48:18.640] mechanisms have existed for a long time. This was not a huge thing until maybe like six months ago or something. Yeah. >> Reinforcement learning just forced them to do that. >> Yes. Exactly. So reinforcement learning uh kind of forced them to do that and so the models were very heavily incentivized to fish finish tasks quickly and parallel tool calling is one

[48:37.839] of the good ways to do that. So if you do reinforcement learning with a very heavy like brevity penalty on on how long uh the task execution is, you can get uh like a lot more parallel tool calling. Cool. So um the final thing I'd like to talk about in this lecture today is evaluating tool use. And so I'm not going to talk about evaluating endto-end agentic tasks immediately yet. um but

[49:08.880] rather talk about evaluating just the tool usability of language models because it's kind of like a prerequisite for language models to be good at um uh good at agentic tasks. And there's a bunch of data sets for this. The most famous one is the Berkeley function calling leaderboard and this has four versions. Uh it started out with version one which was basically um single turn

[49:35.280] uh tool calling. Um it's then evolved through the four versions and now it covers um multi-turn tool calling. It also does have aentic tool calling but this is more um not for like endto-end coding agents or something like that. It's uh tool calling agents and they also have tool calling robustness. So they measure um hallucination of arguments. They also measure format

[49:57.599] sensitivity. So when I talked about like the all the different formats uh they have uh parameters about that as well. So um when you uh go in to evaluate the whole uh stack there's a number of things that you want to uh evaluate. So the first thing is did the language model choose the appropriate tool for the task. So it might have picked like a an inappropriate tool that can't uh allow

[50:27.040] you to do that uh the task at all. Um the other thing is arguments uh which is uh you know whether you you add the right values. Um if you're talking about agentic tool calling you can talk about whether it did it in the right order and then you can uh measure endto-end task accuracy for if you're doing uh agentic tool calling. And all of these are kind of metrics in this leaderboard.

[50:52.559] Then separately from that there's also um efficiency. So like uh how quickly can you solve the task? Like um how many tokens did it take? How how much did it cost? Um reliability. So um you know if a tool call times out uh does it retry appropriately? If a tool is out of order, can it choose a a different one?

[51:15.359] And also um safety. So if you have adversarial outputs where you ask it to use a tool in an inappropriate way, uh can you do this? And all of these are like over the four iterations of this benchmark. It covers uh all of these dimensions. Um yeah, I kind of covered that already actually. So one other uh really interesting benchmark uh for tool calling is uh this open router uh tool

[51:43.280] call air rate benchmark. I don't know if anybody like uses open router or has seen this before. Maybe no. Okay. So um this is for the same model. All of these are for uh I think this is GLM 5.3. So it's like the same the same model and it's measuring the tool call error rate simply the only thing they varied is who serves the model to you. And this is uh

[52:14.960] this is pretty important obviously because you think oh I'm going to use this model maybe you know it's going to be the same regardless of who provides it to me but actually the difference is between 15% and like 0.01 to 0.05%. Any idea uh why this might be?

[52:40.319] There were some uh there were some hints in the lecture and some uh not some hints in the lecture >> is decoding algorithms different maybe someone's using like cheaper version of the model or quantized version of the model. >> Yeah, great great points. So I'll I'll repeat it. So number one is the decoding or the inference algorithm could be different and um one very big difference

[53:03.760] is whether they're using quantization of the model or not or like what level of quantization of the model they're using. So my my personal experience is um uh FP8 models uh FP8 is kind of like the default level of uh quantization for the model um get a lot fewer uh mistaken tool calls than FP4 models because FP4 is like compressing it very heavily.

[53:28.079] It's saving money for the inference provider, but it's it's usually a worse model. There aren't very many FP4 quantizations that can allow you to get the same performance. Another one was uh speculative decoding. Um I don't think we're going to talk about speculative decoding a huge amount in this class.

[53:45.520] Maybe I'll talk about it during long context or actually may there are a few algorithms specifically for agents which are interesting. So maybe we can talk about it. But basically what it is is you have another cheaper model um that predicts what the more expensive model is going to do and then you use that to like speed up your inference.

[54:04.720] um spec lossless speculative decoding probably shouldn't make a difference because it it's like not changing the underlying result of the model. But if they're doing some sort of like lossy speculative decoding uh then that might might cause it to be different. But then you know calling it the same model is also probably a bad uh a bad idea. Uh there's one other thing um that I

[54:27.920] mentioned uh and anybody have an idea this was actually mentioned in the uh in the class today. What can you do to make your tool calls more successful? >> Yeah. >> Constraint decoding. Yeah, exactly. So these different providers might be using different constraint decoding algorithms. Um just practically many many of these providers will be implementing their own inference

[55:05.760] algorithm. So they'll have their own inference algorithm completely implemented from scratch. Um some of the providers will be using an open source one like VLM or SGLANG. And VLM or SG lang support different grammar-based decoding uh algorithms. And so uh some of these providers just might not have that implemented and so they're entirely relying on the language model to do good

[55:28.000] tool calls. Um otherwise uh they might not. A final kind of like boring reason why tool calls might fail is the inference provider might be unreliable. So it might go down some of the time and then the tool call would fail. Cool. Um so these are the um that that's the main thing that I I had for today.

[55:49.280] Um so tool use is basically a layered system. Um you know the tools add capabilities such as retrieval, execution, generation, application. They're what make an agent an agent. Uh but we can't get that uh for free. And um you can uh add schemas to the prompt.

[56:08.480] Uh the models emit calls and then you validate dispatch and match results by ID. And we can add constraints uh like grammar-based decoding. um they don't guarantee semantic correctness. So um if you have like a Python program, the Python program might still be wrong even if you generated uh you know a string that could be parsed as Python. Um and there's a number of uh ways you can

[56:31.440] interface with them like direct rest calls and MCPS. Uh and then we have a lot of systems that um orchestrate dependencies and concurrency and uh allow us to evaluate. So yeah, that that's uh what I wanted to talk about for tool calling. Uh this will be something that is covered in the harness uh assignment or the first assignment where you build your agent.

[56:53.280] So you'll need to need to deal with this. Um but and next time we're going to talk about context management for long context in long context LMS. But um any questions to wrap up? Okay. Yeah. Yeah. And I'm going to repeat in case people didn't hear in the back, but the first um uh assignment for reflecting on the lecture and talking about something you learned in the

[57:16.319] lecture is going to be up on Canvas. So, make sure you uh make sure you submit it. Thank you.
