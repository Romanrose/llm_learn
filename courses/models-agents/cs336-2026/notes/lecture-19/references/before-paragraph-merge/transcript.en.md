# CS336 2026 · Lecture 19 · Guest lecture: Dan Fu

- 视频：[官方视频](https://www.youtube.com/watch?v=9EEm4iMAF5s)
- 字幕：en-US · manual captions
- 处理：连续字幕合并为自然段；每段保留首条字幕的起始时间戳
- 状态：原语言字幕稿，待校对

---

## 正文

[00:05.200] Cool. So thanks so much, everyone for coming. I think you have a pretty cool course here. And thanks, of course, Percy, for inviting me to give a talk. So I think in this class, you're mostly talking about training and how to train these language models, and get to this place where we can have these things that can talk back to.

[00:29.240] And today, I'm going to talk a little bit about once you have one of those models, what it looks like from the other side, what it looks like to actually serve these models, do inference, turn these things from say, electricity, into tokens, into intelligence.

[00:46.580] And also what are some of the fun research problems and research things that you can do when you look at it from that standpoint. I'll start with some of high level motivation. I think one thing that's become abundantly clear to all of us is that we are really going through almost a new industrial revolution in terms of these models and their capabilities.

[01:09.090] These slides I made during my job talks two years ago. So the exact examples are going to be pretty old, but you can do human-level text generation, code generation, Cursor, Claude Code, GPT 5.5, not just 4. You can generate images and videos or understand images and videos and process them.

[01:31.930] You can start to understand new modalities. So we're starting to see some of the applications and the sciences in bio and health DNA models, all these sorts of things. One of the things that has really been driving my research for a while is the question of what has made these advances possible, and how can we improve on them in the next generations?

[01:52.650] And one abundant driver of these capabilities is really scale. So again, this is at this point, are pretty old figure but these models have really scaled up in massive ways. So in 2018, at the beginning of my PhD in antiquity, these were hundreds million parameter models at their largest.

[02:12.830] And we were like, oh my God, these things are pretty crazy. By 2019, we thought that they were too dangerous to release, that's GPT 2. I think in this class, you can train a GPT 2 quality model. I'm not sure if you did. If you tried hard enough, you could.

[02:29.550] And today, of course, you have open source models that are a trillion parameters and more. Frontier is probably at 5 to 10 trillion parameters. It's pretty exciting. With these, you have a bunch of new capabilities like chat, writing code, analyzing complex text, doing your homework for you, et cetera.

[02:50.410] What's really remarkable about this is that this transition is happening faster than we think. So certainly, faster than I thought at the beginning of my PhD a few years ago. So I think one really apt analogy and the dates actually match up in an interesting way.

[03:06.960] So in 1902, there are 130,000 working horses in Manhattan. So these are horses that you don't just have around for giggles, but you actually have them because they play some key role. And they would-- these horses would produce-- each would produce pounds of manure a day, times 130,000 horses, you have a real manure problem.

[03:27.840] So in fact, there were entire conferences that were just gathered around the question of-- entire academic conferences around, what do we do about all the poop that these horses produce? So in 1898, they actually had one of these in New York. And their conclusion from that conference was, there's nothing we can do about the horse manure.

[03:44.670] You just have to hold your nose and deal with it. 10 years later, by 1912, cars had already outnumbered horses in Manhattan. So that 10 year transition, you saw these things that have been around for centuries start to be replaced by cars. And I think for us, for language models, for a lot of the stuff that we do, that 1912 moment was probably last year.

[04:12.690] So at least for me, last year, I started writing the majority of my code using these language models. Most people in my team do it. I tell all my students to do it, except when they're doing their homework. But this is a really exciting transition that we're living through.

[04:31.750] One of these things that is really driving this is, a lot of the scale is driven by GPUs. So in a very real sense, you could say GPUs are the new oil. This is again a older announcement, but you're seeing hundreds of billions of dollars and more of investment into GPUs.

[04:50.950] History rhymes in interesting ways with similar things, but there are entire countries-- entire sovereign wealth funds that are making these things a major part of their piece. And one thing that is really abundantly clear is that inference is really the piece.

[05:12.660] So you can think of inference as the engine that turns electricity into intelligence. So the same way that oil is only useful in a car, if you can have an engine that turns that oil into useful kinetic motion, inference engines, GPU kernels, these are the things that really turn-- that really turn these GPUs from sand, like Percy said, into something that we can use today.

[05:38.560] And I think that's clear. So if you think about it, these machine learning models, they're really just DAGs of operations. There are some mathematical object that exists in the ether. The inference engines, the GPU kernels, all these pieces, these are the things that you actually have to program and map them down to ML operations.

[05:54.620] I think you do some of that in this class. I think you implement some flash attention. So some training side. But there's a whole world of complexity when it comes to inference and the inference side of things. So if you take away nothing from today's talk, I hope there's one thing which is, if you understand inference and understand the inference engines,

[06:15.220] if you understand the GPU kernels that underlie a lot of the core technology, you can enable full stack innovation in machine learning algorithms. So I'm going to start with, in today's talk, a high level overview of the lifetime of a token. So when you make a request to one of these models, what happens to that request, how it goes through the entire inference service,

[06:38.300] what are some of the interesting choices you have to make. And then I'll dive deeper into two more research projects around, if you take certain pieces of this system, what are questions that you can ask and what are some things that you can do? Before I get into all the technical details, I'll quickly make a plug.

[06:58.678] So I'm here representing two organizations. So one is UCSD, where I have a small lab, and some of their work is represented in this talk. Then I'm also representing together who did a bunch of the work that's represented in this talk together as an AI cloud.

[07:14.950] So there's GPUs, Inference, Fine-Tuning, and all the rest. Heavy research background. So including Percy, I don't think you can see my mouse, but he's on the screen. And then we've got a big research presence behind that, and behind a lot of the things that you're going to see in this talk.

[07:34.130] All right. I'll start by giving a high level overview of a lifetime of a token. So when you make a request to a inference system, what are the different pieces that are going to go through? And these slides are cribbed from a presentation that my student, Austin made from his experiences together.

[07:55.340] I'll make a note that all of the slides are completely AI generated from Nano Banana Pro, but they're pretty good as long as you don't look too closely at the tech. So I'd say, at a high level everything is correct. If you look very closely, you'll see things that are very wrong.

[08:10.820] This is a overview of all the pieces of an inference engine. So I'll give a high level description of how it works. So you get a request in. The first thing that's going to happen is that the request gets scheduled to various different GPUs. You might have disaggregated prefill and decode on different machines.

[08:32.539] You'll run that request against a KV Cache to see, have I seen this request or versions of this request before? Is there some compute that I can actually save? Then you'll start executing the core machine learning code. So here are new tokens. Here are new operations that we need to compute.

[08:53.740] There are various optimizations that you can make. So you can split that computation across different machines. You can parallelize across different nodes. You can parallelize it within a node across different GPUs depending on the size of your model, depending on how you can split up, split that up.

[09:09.060] And I think one of the exciting things is that, as we are-- as the hardware is developing, we're actually going to start to see more different choices that you can make there. But once you make all those choices, once you execute all the code at the end, you get the tokens that you can say, hey, Chad, what did Percy mean when he said linear regression because I

[09:30.620] skipped that day in my class? And you get this whole end to end experience. One of the things that I think is useful to start thinking about is, what do these different workloads look like? And there's quite a bit of different things. So this is one of the sites where if you look too closely, I think some of the fives turned into S's.

[09:55.350] But one of the things that you want to think about is, when you're actually serving production traffic, it doesn't necessarily look like-- certainly, doesn't look what the type of tokens that you see during training. But it also doesn't look like if you just made up a traffic workload in your head.

[10:12.130] So what is the type thing that we typically see? So for a particular workload, you'll see a particular distribution of input and output tokens. So let's take a coding workload. So let's say you're somebody like Cursor, where you have your whole code base is available to the agent and you're asking questions about it, typically, what that will look like,

[10:33.750] is that you'll have a long amount of input. So tens of Thousands of input tokens. And then depending on how you've trained your model, the model might output some amount of thinking tokens, or it might output some short input in. And this will change based on workload.

[10:50.500] It'll change based on model. So a coding workload for example will look very different from a summarization workload, or a narrative summarization. So if your work involves pasting entire books into a chat window and then talking back and forth to figure out what's happening, that's going to look very different than a standard chat thing.

[11:12.900] So if you just go to chat and say, hey, explain to me first order calculus or whatever, that's going to have very different workload shapes. The way that we use language models today, there's very turn-based agentic workflows. So when you're coding, you go back and forth with your coding agent, say, hey, do this.

[11:31.340] No, I didn't mean that, do that. Your coding agents themselves can iterate on the language models quite a bit. So they might invoke some tools and say, grep search for something in my data-- in my code base, and then take that and go feed it back to the model.

[11:49.040] I might try to do an internet search and look up this thing that my user asked me. So typically, you have these multiple turns in your conversation. Now, another interesting piece is different applications will have different times. So if you're in a fast, interactive chat based loop, or if you're talking on your phone to ChatGPT in the voice mode, you

[12:10.680] might have relatively quick responses. If on the other hand, you've put together an agentic workflow where you say, hey, go do this for me, I'm going to leave you alone and just iterate on your own, you'll have a different cadence. If at some point your agent gets stuck and say, hey, help, I need to ask for advice, and you don't notice it, there might be another gap between turns.

[12:32.920] So all of these things start to define what your workload looks like. So how many new tokens do you get in it every time? How many tokens are you going to generate? How long is my session? Am I a very sticky user who keeps going back and forth with my Claude Agent, or am I a user who's just going to ask one question and then leave and come back the next day?

[12:54.410] And of course, how long between turns do you have? I, for example, have a chat that I've had with a ChatGPT agent about how I should set up my workout and my workouts week to week. And I interact with that chat once every other week. So that is a very different traffic pattern than some of the other ones.

[13:16.527] And then of course, depending on your application, you might have different targets. So if you have a interactive application, you might say, I want to get the first tokens back in less than a second, so that the agent can say, hey, I'm thinking and I'm going to say blah de blah de blah.

[13:31.250] Or I might say, I know I'm going to be generating 500 tokens, and I want that whole response to come back within a certain amount of time so that my user can read it fast enough and all these pieces. So as that-- when that request comes in, there are a few basic pieces that come in.

[13:52.800] I'll rest a bit on the prefill and decode piece in a little bit. So let's say you have some amount of text that comes in, the first thing you're going to do is you're going to tokenize it. I think you're all familiar with that. But then once there, you start getting into a somewhat complex scheduling regime because you have to ask questions like, have I seen these tokens before?

[14:12.320] Can I just look up some of the activations in a cache? And then you get to basically, these two major pieces of the actual machine learning computation. These are called prefill and decode, and they're very different beasts. So prefill means let's say you have 10,000 tokens that you've never seen before, and you want to go compute what the activations and what the logit should be.

[14:37.050] So 10,000 tokens in, one token out. That's a very compute bound operation. So that actually looks pretty close to the things that you guys have been looking at for training time. So when you're training, you have some large amount of tokens. You write your flash attention kernel when you run your training loop.

[14:51.630] Prefill is very similar. You just don't run your backwards pass. And then you have this thing called decode. So decode is when you're then just generating one token at a time. So you pass in these 10,000 tokens. It's like, hey, here's my code base, tell me what function ABC does?

[15:06.470] The model is going to process the whole prompt and then start generating one token at a time, maybe three or four tokens if you have speculative decoding working. And if you think about that operation-- so every time you generate a new token, you then have to run that back through the model.

[15:21.250] If you do the math on that, there's actually not too many flops that you need to compute. So it's going to be a relatively light computation, but it's going to be very memory bandwidth bound. So what that means is you're going to be running-- you have to load up the model every time just to generate a single token.

[15:37.910] At the end, you get-- at the end of that model pass, of course, you then have a single number that represents a token that then gets turned into a string. You probably do a little bit of processing on that. So you look for stop tokens. You check. You might run a safety check to say, oh, is my user trying to hack into the system in a bad way, et cetera?

[16:00.650] And then at the end, you get the tokens. And the inference engine is really running in this loop, waiting for these requests to come in. So it's waiting-- so it's running this scheduling execution token sampling loop and repeating. So I'll get into a little bit of-- so now we can take one step deeper and start to look at, what does it look like when you have

[16:27.950] a system that is processing many different requests at a time? So we have this phenomenon called-- this technique called continuous batching. So the way to read this figure is that it is time is flowing downward. So as you go down, there are new requests that are coming in.

[16:44.880] So let's say, if we go to step one, you have some long requests. You have a user that is asking to analyze some long document, and the engine is going and generating a bunch of tokens out. You might have another request comes in that starts to take up some resources.

[17:04.339] So these resources are first compute resources. You have to run things over multiple requests at once. They can be memory resources if you're filling up a KB Cache. And so you'll see these multiple requests happening at the same time. After a step, that short request might finish and you get a new request that comes in, and maybe it's running for a couple steps.

[17:29.330] If you have another request that comes in, maybe it's another very long request. So that's going to be that orange one in step four. But maybe you don't have enough GPU memory. So you need to store all your KV Cache on your GPU. Maybe you've run out. You might start queuing for some reason there.

[17:45.450] Then once that long request is done, you can start the new request, and then, et cetera, you can watch it run. So already, you're seeing some of the complexity when you have many different requests living in a system and how it goes on. One of the pieces that's quite important is this thing called a KV Cache.

[18:08.370] So the way to think about this is that you probably have a lot of users who are saying, hi, ChatGPT or hi, Claude. And then theoretically, you don't need to compute new activations and run that again for every single user. Or if you have a long book that the user has passed in, you compute, you run the prefill over that once,

[18:31.150] and then the next time you get some addendum to that request. The next turn in the conversation, you don't need to compute the whole thing again. So we have these mechanisms called KC Caches that use prefix sharing, that say, hey, I have this new set of tokens that comes in, use a very traditional data structure like a basic tree,

[18:50.570] look at which tokens have I seen before, which tokens are new, and then basically, do a lookup of what those activations are going to look like. Once you actually have the computation on the GPUs, there's various ways to split it. So I'm not sure if you talked about this too much, but let's say you have a trillion parameter model and you're running on 280 gigabyte GPUs,

[19:16.433] you're not going to be able to fit the whole model onto each GPU. So there are various ways that you might split it. So you might take every tensor and split it four ways across four GPUs. This is called tensor parallelism. Or today, we have a lot of the state of the art models or a mixture of experts models.

[19:35.120] So you have these individual experts that get selectively activated depending on different tokens. You can split those across different GPUs. The choices that you make at this point will determine what are the bottlenecks. How many GPUs do you need to run your model?

[19:52.140] How many sessions can you serve at the same time? Et cetera. One of the big things that happens is that we tend to split prefill and decode onto different GPUs, different sets of machines, and that's because they have very different compute bottlenecks and compute characteristics.

[20:11.840] So prefill looks a lot like what you guys do during training. You just run it. It's very flop heavy. You can really use the most out of your GPUs. Decode on the other hand is very memory bandwidth heavy. Because you're not doing that much compute, but you still have to load up all the model weights at the same time.

[20:31.360] These things will also take different amounts of time. So prefill will typically take a lot longer than a single decode step. But you're going to be running a lot more decode steps, because you will run prefill once for a prompt, you'll run decode once for every token that you generate.

[20:46.190] So a very basic optimization that pretty much we've all started adopting is that you'll run prefill on one set of workers, decode on another set of workers, so that you can specialize those two computations to different pieces of the stack. And turns out, there's a lot of innovation that you can have when you have these splits.

[21:05.722] Some things that you might have heard of, that when NVIDIA bought Grok. So NVIDIA, the King of GPUs, buys this new inference chip. One of the reasons is that the decode workload is so different from prefill workload, that if you're looking at code, you can be using very different chips.

[21:24.910] So for example, in the next generation of hardware, NVIDIA is planning on using its GPUs for the pre-fill side, using these LPU Grok chips for the decode. You see similar things with Cerebras. So OpenAI has this compute partnership with Cerebras. It's another chip that's much better at decode.

[21:43.350] There are other companies like SambaNova and so on, that are also making bets on various parts of this space. Here's a fun one, an interesting one. So when you actually start deploying these inference engines at scale, so when you're starting to serve trillions of tokens or more a day, you start to get some pretty nasty bugs.

[22:05.690] So this is a set of bugs. I think most of these happened in late last year with some of the open source inference engines. And basically, one of the characteristics of these large scale systems is that something that will work well at a small scale will inevitably start breaking at a large scale.

[22:28.820] So we're talking events that happen with 0.001% of the time or less. Some of these can be so NaN. So sometimes, you'll have a kernel that is very slightly wrong. But the conditions for triggering it are very rare. And you will start having some of your logits turn into NaNs halfway through the computation.

[22:53.740] When that happens, we figure it out that the model starts outputting the same token. So I think some model, the output just started saying, hi, hi, hi, hi, after a while, or start outputting exclamation points and you get caught into these loops. Another model, at some point, someone made a change to how you're handling tool calls.

[23:14.620] So tool calls are when the model says, hey, I want to make an internet search or something like that. So the model will actually say, go do an internet search. And then your end harness has to then go use old fashioned code to do the internet search. At some point, those tool calls stop being processed correctly in one of the engines.

[23:36.710] And the symptom for that the completion lengths shot up because the model would say, hey, make an internet search, and then it would usually-- when the model is behaving correctly, it says, hey, make an internet search. I'm done. Go return to the user. Go do that, whatever.

[23:53.190] But in this case, it wasn't returning correctly. So it'd say, hey, make an internet search. Hey, make an internet search. Hey, I don't know why there's no internet search going on. It would just get into this very long doom loop for tens of thousands of tokens.

[24:07.250] There's another one that-- this one was interesting because it actually took out a number of insurance providers at the same time. And it actually got blamed on a quantization issue. But actually, what was happening was a much more subtle bug where the model would just suddenly, randomly start to output Chinese characters when it had no reason to.

[24:32.320] So for some models, that sometimes there's some speculation, oh, they must have fine-tuned on a Chinese model because my model suddenly starts. I ask it a question in English and starts speaking back to me in Chinese. Actually, what was happening is that there was just an off by I error in one of the kernels, and it would be a very subtle bug.

[24:53.000] So sometimes, you would read in some extra uninitialized memory space from your GPU, run it through retention, and then at the end of that whole process, you get a random Chinese character. Then the model will go, why did I start suddenly thinking in Chinese?

[25:09.660] I must be-- the user must be asking me a question in Chinese, and then it will just go veer off into Chinese. So sometimes when this happens, it's because the model has legitimately been trained to say-- to think in Chinese. Sometimes, it can just be an off by one bug in somebody's code.

[25:31.780] Some interesting things that are starting to happen in a lot of the more advanced inference stacks. So a major piece of running large production systems is that you want to have as large of a KV Cache as possible. So it is best if you can cache requests from many different users or from the same user across many different sessions, and be able to run as many sessions as possible.

[25:59.100] You first started this by storing your KV Cache on GPU, and then you quickly run out of GPU memory. So the next, you can start storing into CPU DRAM. So if you're paying attention to Jensen's keynotes, he's recently started getting very obsessed with CPU performance.

[26:18.030] One of the reasons is because a past generation of CPUs was actually really slow. And as a result, started bottlenecking a bunch of very important workloads. And as a result, you start to pay attention because if you're $500,000 machine is being bottlenecked by the $1,000 CPU that you purchased to put on top of it, that's not a great place.

[26:44.013] One of the reasons that can happen is that you might be storing your KV Cache on CPU memory. And so you really care about the speed of being able to read that KV cache back. Next, you might put more KV cache onto the disk itself. And then you start caring about SSDs and SSD space.

[27:01.590] Again, you've probably heard these rumblings about OpenAI buying up all the SSD, all the DRAM in the world. Part of the reason is for stuff like this, where you want to store as much stuff in your KV Cache as you can. And then of course, when you're actually building your engine, there's this complicated dance of, I haven't seen these tokens in a while.

[27:22.820] Maybe I'll evict it, send it on to the CPU, or send it into disk, or send it into some other global store. When I get a new request in, I have to go look. I have to go wait for those to come in, fetch them, load them up into my thing, and then we're happy.

[27:39.680] It's kind of CPU offloading. Is it like a special kind of workload that gets offloaded? For something fast, you don't want to do this. Time to hit a SSD is very long. Can you repeat the question? Yes. Yeah, so the question is so for this offloading, is it a particular type of workload that you offload?

[27:58.480] So here, we actually get to some pretty-- i'm sure none of you guys have taken an operating systems class. But you should take your operating systems classes-- you actually get to some pretty classic scheduling things. So you could have this diagram except for the GPU things on the right.

[28:14.340] Looks exactly like a operating systems diagram that you might have seen in the '70s or the '80s. Because we used to have this problem, where if you opened up too many applications on your computer, you would run out of CPU memory, and then you'd have to put those applications onto the disk.

[28:32.640] And it is exactly the same workload. So ideally, here, actually on the left side, the Nano Banana hallucinated evictions for least recently used which is actually a pretty decent heuristic. There's probably some OS paper somewhere that says that LRU is within 2x of what you can do.

[28:51.820] That's optimal. Of course, the best thing that you want to do is, if you could predict the future, you would know, oh, I'm about to have a request come in of a particular kind. Let me go prefetch that memory in. It might actually be possible to predict the future.

[29:07.590] So for example, when you go into your chat app and you bring up some old conversation from a month ago, that's a very strong signal that you're going to go start asking a question about it. You might then want to go load that up onto a GPU. But in a perfect world, you predict the future.

[29:24.750] If you can't predict the future, you use various heuristics. And really, it's a question of how much traffic you want to put onto your GPU footprint. I've never talked to anybody who wants to put less traffic onto their GPUs. So I think Modulo or subject to those SLAs that we splashed up at the beginning, you want to serve as much traffic as you can.

[29:54.010] Some fun things that are starting to happen. So in the last generation of Blackwell GPUs, NVIDIA started putting together these new GPUs called NVl72 Grace Blackwell chips. So these are 72 GPUs that are connected with really fast interconnects. And so you start to do things like, how can I split my trillion parameter model across all 72 GPUs?

[30:18.180] Does this make any sense? What does it buy me? What happens? How do I start to think about fault tolerance? So these things can fail a lot for various different reasons. One reason is that the connectors are flimsy. They're made of plastic, not made of metal.

[30:36.400] So if you like jam the thing in too much, then your cables are going to bend the things a little bit, and then you get really flaky NV links, which is a whole thing in itself. But what happens when-- so this is the AI generation. So let's put a fan into the chips, which doesn't quite make sense.

[30:55.088] One of the things that you want to start thinking about is, if I've taken a model split it across 64 GPUs, and I'm serving production traffic against millions of users, trillions of tokens. What do I do when a single GPU goes down? Is there some way to make that fault tolerant?

[31:09.800] And there's a lot of fun things to think about there. And then, of course, you're starting to see these models have a million contexts or more. How do you actually process it? Do you split that context across many different GPUs? How do you do these different things?

[31:29.700] So I want to dive-- just very briefly highlight one set-- one example of an optimization that you can start to make when you start looking at this whole process from a systems level. So this is a piece of work that we put together a few months ago called Cache-aware Prefill-decode Disaggregation.

[31:51.220] It's a very simple optimization. It's two lines of code in the routing layer, but can actually make a pretty big difference. So the basic idea is, you have all these requests that are coming in. Most of them are going to be turn by turn requests in a conversation, where somebody's already started a conversation.

[32:10.710] But let's say your average conversation lasts 10 turns and then the user goes away, that suggests that 10% of your requests are going to be very fresh, very new requests. So when you have a new request that comes in, that's going to be thousands of tokens.

[32:24.850] It's going to look very different. It's going to be a lot more expensive to compute. You don't necessarily want to put that prefill against a short conversation where you're halfway through conversation. So someone paste in a book and says, hey, talk to me about this book.

[32:40.450] You don't want that running at the same time as someone who's midway through a conversation, like, chat explain to me why 1 plus 1 equals 2. And chat is like, 1 plus 1 equals 2 because numbers and whatnot. And you're like, oh, I don't get it. You don't want that very short question and answering to happen in the same time, on the same GPUs, as the very long request.

[33:06.240] So you can put together this really simple router that says, OK, if we have a new request that comes in that's very low cache hit rate, send it to one set of GPUs so that those can all process things together and then send all my other warm requests to another set of prefill nodes.

[33:22.488] It turns out if you do this, you can get up to 40% faster serving with these very, very simple optimization. So that's one set of things I'd say, the way that I would characterize where we are in terms of the research and these techniques is that we're very early.

[33:39.860] So this is the type of thing that in 10, 20 years, they're going to look back on and be like, oh, why are these guys talking about this? Isn't this already obvious to folks? But really, it's because we're starting to see these things, running them at production in new ways.

[33:56.990] Seeing these new bits of traffic in new ways. All right. So that was a overview of the inference life of a kernel. Now I'm going to talk about two interesting research projects that are very much inspired by some of the things that we see when serving things.

[34:17.810] So this first one we're going to be talking about language model decode, and how you can make it go a lot faster with these things called mega kernels. This is a collaboration between Stanford and Together. So the fundamental challenge when you're running Decode.

[34:34.429] So Decode is the process by, you've processed your prompt and now you're generating one token at a time. The fundamental challenge is that you have to run the whole model to generate a single token. So that means that instead of using all this big parallelism that you get with a GPU that you can do during pre-filler training, you've

[34:54.850] now turned this massively parallel system into basically a glorified memory loader. And one of the things that makes this extra challenging is that the way that we typically write down kernels and run a model is that we will write down kernels and program things one operation at a time.

[35:16.370] So you guys can probably understand why this is so. Kernels tend to be pretty challenging to write. I'm sure you guys all had a lot of fun writing flash attention. But that means that typically, what we do is we look at all the different operations in a language model, and we will run-- we will write a single kernel for that operation at a time.

[35:36.730] So this makes things a lot easier to program because you just have to write your Norm kernel, your matmul kernel, your attention kernel. But you end up seeing, it ends up introducing a lot of downtime into your system. So this is an example of what it might look like when you're running inference across your kernel.

[35:59.720] So this is obviously a cartoon, but the example is drawn from a particular attention inference kernel. The way to read this is that on the x-axis, you have time. So time is flowing from left to right. On the y-axis, you have all the different little streaming multiprocessors on your GPU.

[36:20.800] So on a H100, there are 132 of these. On the B200, there's 148, et cetera. The bars indicate useful work. So when there's a bar here, one of the processors on the GPU is actually doing work, and the empty space is just waiting. So you're just waiting for other operations to finish so that you can have something else go on.

[36:44.980] And so basically, you get into this position where no matter how well you try to write the kernel, you're always going to have downtime in your GPU. So you're going to have things like kernel launch. So a kernel lock or kernel teardown, that's these big gaps in the red and the yellow.

[37:00.800] You're going to have these things called tail effects. So this is just the same way that if you have a short prompt that gets processed with a very long prompt, this same thing goes all the way down to the basic attention operation. If you're processing a batch of inputs and one input is very short, one input is very long, you're going to be waiting for the very long input to finish.

[37:22.390] And then because you're running these across multiple kernels, you will actually start to see these gaps between kernels start to add up. So one thing that we put together to try to solve this, is thing called a Megakernels. So this is basically saying instead of treating each operation in the model as its own operation writing kernel for it, instead, let's write a single kernel

[37:44.430] to cover multiple operations at once. This is similar to the fusion that you see in flash attention, except done more aggressively across a larger number of things. And in particular, what it does is it turns a GPU from a single device-- a single operation is you start thinking of the GPU as a massive distributed system and saying, OK, I have all this work that I need to get done.

[38:07.650] Some of it has dependencies on other stuff. So that red stuff has some dependencies on some of the green bars. How can I schedule it? How can I distribute the work to maximize my GPU utilization? If you do this just to the attention inference kernel, you get 30% to 70% speedups.

[38:27.910] And then the nice thing is that you can actually do this to the whole model. So this is one layer of a Llama-1B model. So here, we've basically taken the entire layer and put it together into one kernel. If you look at all these different bars, you see things are overlapped in really weird ways.

[38:46.360] That's because we are now starting to overlap a weight load from the next-- from the layer into the attention, or starting to run parts of reduction before the attention operation is over. Here's one interesting example. So here's one thing that you can do.

[39:07.700] So if you look at modern LLMs, you have the attention layer. You have the QKV projections. You're going to add some rope scaling to it. So that's these blue lines. So those blue lines are QKV plus rope. And then the orange lines, this is the beginning of the attention.

[39:24.660] So one of the insights is that you can start loading in your KV Cache into your attention before you're finished with QKV, and particularly, during decode. So these orange bars with some of these circles, you start the KV Cache load while the QKV plus rope is still running.

[39:42.360] And then once QKV is done, then you have your new query tokens. You can run the rest of the attention operation. So basically, when you have this fine-grained control of GPUs, you can start some operations before others are over. Here's another one. So again, the orange is the first part of the attention computation.

[40:05.190] The red is the O projection that comes after attention. And you have your O projection. Start loading the weights before your attention operation is over. We put this together in a very relatively complex CUDA framework with basically instruction and instruction based abstraction, where we can implement each sub-kernel in its own file, and then have a big virtualized shared memory

[40:32.650] system to orchestrate the running of these operations. And to do this, we put together this library called ThunderKittens, which is one of these kernel writing libraries. You can think of it as almost like Triton, except more low level, a lot more fine-grained control over things.

[40:56.820] The payoff is you get near speed of light decoding inference. So these numbers are actually a lot better now. But the Megakernel shown by this bar in teal, and you can see it runs a lot faster than some of the other state of the art engines. And on the H100, it's achieving 72% bandwidth utilization, which is near the speed of light on the GPU.

[41:18.720] So if you just ignore all the complexities of what we're doing here and say, how fast can the GPU physically go to do this operation? We are pretty close to 72% of that speed of light. So one interesting bit there is a takeaway from that section, is that, if you have very deep control of the kernels and the understanding of the hardware,

[41:40.460] you can start to enable very different compute paradigms. And all these things, you only see when you start playing with inference at a deep level. And now, I'll talk about something that's a little bit new. So this is now getting into the realm of new architectures.

[41:58.780] And I'm going to be talking about this new model called Parcae. So this is some work that comes out of my UCSD lab led by Hayden, and then also in collaboration with these two folks, Zachary and Taylor. So I'm going to come back to this. So at the beginning of the talk, I talked about, hey, all these new capabilities are coming

[42:17.877] because you're starting to scale these models, and parameters, and data. With Parcae, we wanted to ask another question, which is, is this the only way you have to scale? Or is it potentially is there potentially something else-- some other way that you can get this quality?

[42:32.660] And with Parcae, we wanted to-- this was basically our take on a technique called loop transformers, where you take some blocks of your transformer and you run them in a loop. So instead of having your tokens go all one layer at a time through the model, at some point you say, hey, as you're going through, just send it back through that loop at a time.

[42:54.750] You're going to see, there's a couple different pieces here. So one is, we use some State Space Model theory, some SSM theory to stabilize this operation. Naively, if you just run this and let the thing train, we saw that the thing was going to blow up. And then the other thing is we started to see some interesting scaling laws that suggest that you want

[43:14.030] to be scaling the recurrence of these recurrent models as you increase the data. So in order to make the best use out of your parameters, you want to actually be reusing them somewhat. First, I'll talk a little bit of motivation of why we found this looping problem to be very interesting.

[43:35.120] So the basic idea is, let's say you have some activation that's going through part of your model, at some point, it hits these loops blocks and it's just going to run the same activation. It's going to run through that same layer some number of times. So that purple block is the recurrent block.

[43:51.400] And then at the end, you get the thing that comes back. So there are some advantages of this. So you can keep your parameters constant, but it gives you a dial to increase your flops. So if you think that flops-- more flops equals higher quality, this is a way to increase your quality without paying a higher parameter cost.

[44:12.040] Another thing is, there's this old work-- old is a relative term from a few years ago-- that suggests that you actually get higher expressivity-- their expressivity. There are things that you can't express with the same number of parameters, that you can express with these looped models.

[44:32.560] And one of our driving questions was, what's the best quality per parameter? What's the best intelligence per parameter? Or intelligence per parameter and data that these things will allow you to do? There are some promising initial results. So this is a paper from Tom Goldstein's group in Maryland that suggests that hey, this thing might be better than transformers.

[44:55.320] These are some results on the Arc tasks. And there's also a bunch of Twitter hype, because about a week before we released Parcae, some dude from OpenAI said that Claude mythos is a recurrent-- is a looped language model. I don't think it's right. I think he was just making it up.

[45:12.380] But as a result, it really blew up in Twitter in speculation right before this. Eventually, he had to write this blog post being like, hey, my bad, I just made that up. None of it's true. But it was sufficiently interesting to go. So we were working on it before this Twitter hype, but I think there was something interesting, something interesting to look at here.

[45:38.250] Now, one problem with these looped models is if you looked at any of them and you tried to train them, and then you changed anything about the training algorithm at all. So if you change the learning rate by a little bit, you'd suddenly start to see these models blow up.

[45:52.350] So if you did a simple thing like a learning rate sweep, you'd see nine times out of 10, this model just isn't going to converge, it's going to blow up. You're going to get NaNs. You're going to get these big loss spikes. And so we were saying, hey, there seems to be something wrong with this.

[46:06.393] So if you're training a model and you're actually scaling it up, and you see there, these big loss spikes, that suggests something has gone very wrong with your training process, you should take a deeper look and try to figure out what happened. In previous work, there were some hacks like you can put norms in every layer to figure out what's happening or just pick two--

[46:25.250] the learning rate of 2e-4. Don't pick any of the other learning rates. But we were thinking, hey, the existence of these loss spikes suggests that there's probably something more deeper going on. And so we took a bit of a mathematical state space model-esque approach to the stabilization question.

[46:47.500] Our basic insight was, you can look at this process. So actually, if you look at this process, you try to think about how to analyze it analytically. It's going to be very complicated, because this big R block has tons of parameters. There's all sorts of nonlinearities.

[47:05.040] There's a Softmax, there's GELU, and RoPE, and all these other things. So if you try to analyze it analytically, it's quite complex. Our insight was, we were just saying, OK, let's actually just look at the residual of this thing. So how is this activation changing from block to block?

[47:23.980] Our first empirical observation was hey, it actually doesn't change that much. So each of these residual blocks is changing the vector a little bit, but not really having a massive impact. And as a result, how can we-- so maybe we can actually model this. Maybe we can actually look at what's happening more deeply.

[47:46.340] And so what we did is we went and wrote down a dynamic system over this residual. And when we did, we realized there's a couple pieces in here that when you look at how you write down the model, might look relatively benign, but actually end up being a huge bit.

[48:04.060] So what we did was we said, OK, there's all this nonlinear stuff, there's this attention, there's this GELU, there's this big feed-forward network with the intermediates and stuff, we're going to all put that into a box. We're just going to call that R. And this R is going to be some big nonlinear thing.

[48:23.020] But we're going to put it-- just take it to the side. What you're left with is these A and B matrices. So this B matrix is some transformation over your initial vector. So what is that first vector before you start the loop? And then this A vector is-- this A matrix is how do you transform that residual in each loop?

[48:50.630] And what we did is we said, hey, this simple thing, if you take all the complexity of the transformer, stick it to the side, you have a relatively simple way of looking at all the previous loop transformers. And in previous cases, you do end up making some pretty normal decisions.

[49:05.970] So in one case you just say, oh, you just treat it as the identity. You're just going to add things. In another case, it's a fully learnable matrix. And then we said, OK, what happens if we just so-- the residual-- we observed empirically, that these A and B matrices are actually dominating the magnitude of this equation.

[49:30.880] What happens if you just drop that complicated nonlinear piece? What do you get out? Well, you get out actually a pretty simple system that if you use high school calculus, you can just solve it to figure out what the answers are going to be. So here's the closed form solution.

[49:46.240] You can actually compute what is, given what the initial activation is, and what that initial injection is, you can actually just empirically compute what the activation is going to look like at Step T plus 1. And you notice a couple of things. So this thing is dominated by these A matrices.

[50:08.040] And especially, this A matrix that you are powering up to a large degree. And from here, what we realize is that there's this quantity called the spectral radius of this A. So spectral radius is basically like another word for norm. One way that you can look at this is that, you're taking this matrix.

[50:29.630] You're powering it up to huge amounts. If this matrix can learn to be something like-- let's say that this matrix-- if you go to scalars, imagine that this matrix is 2. And then this T is like 16 or something, you've now taken this activation, you've blown it up to 2 to the power of 16.

[50:47.370] And it's really big. And this starts to explain some of those big loss spikes. And in particular, what we found is that, the choices that you make for these A and B matrices that people have made in these previous papers are either-- we call them, marginally stable or unstable.

[51:05.370] Unstable-- make the system unstable. And so with Parcae we said, OK, well, we figured out this thing where if you take this particular look at it, and you let these A and B do whatever they want, you're going to get things that really explode. What if we just constrain A and B such that if you run the math they're not going to explode?

[51:27.290] So for A, what we did is we said, OK, we're effectively going to make that A matrix a negative diagonal matrix. So if you power that up, the term eventually goes to zero, so it doesn't blow up. This B matrix, we're going to put a-- stick a really simple linear norm against it, because this B matrix actually, only gets applied once and doesn't really blow up.

[51:48.570] E can be the spectral radius. It's now going to be less than 1. It's now actually going to be a stable system. And now if you go train this model, what we saw is that you actually saw stable loss curve. So Parcae is this stabilized thing where we re-parameterize A and B. You can see that even with this the 6e-4 learning rate that was so bad for the other models,

[52:11.030] you actually got a stable model at the end. And you see that with doing this, you can naturally constrain the state norm of the activations. So two pieces here. So that orange baseline is just a completely unconstrained model. You can see it blows up, goes to 10 to the 19th.

[52:29.700] This blue line is actually a model where you are applying a norm to it. So what happens here is that the model is actually trying to expand the activations because it's saying, oh, with more room, I can represent different things better. I can put these different concepts further away from each other or whatnot.

[52:52.482] And then you're applying norm to it to take that big thing that's trying to expand. Then you try to norm it back down to one. And then you have this big-- these two pressures that are fighting against each other that manifests in loss spikes. So even though on the right, your norms are very good, you're not seeing the activation actually blow up.

[53:10.820] You do see that the loss can do some pretty gnarly things. So basically, there's this pretty simple change in the activations can stabilize the training, stabilize these recurrent loops. So it's not only a more stable system, you actually also get more higher quality models.

[53:31.550] So this is a table where we are comparing Parcae models against a previous loop transformer called Recurrent Depth Model. So you can see higher performance across a variety of applications. So you see Parcae outperforms the previous models and also outperforms strong transformer baseline.

[53:51.250] So this transformer is one of the nanochannel ones where a bunch of people are trying to just get it to learn as fast as it can. And these Parcae models, if you take that same basic transformer architecture, start looping it, and then stabilize it, you get better perplexities, better end to end quality as well.

[54:13.030] And then one-- and then we started to run some very basic scaling laws here. And here, our question was, OK, this is really, really cute. You can do this looping thing to make things better. But really, should you-- is there any evidence that there's something here that we want to be doing looping more aggressively?

[54:32.590] So here, I'll take a step back. A few years ago, there was all this work as we started to enter this regime where you wanted to scale up all these models, a natural question is, should I make the models bigger or should I just train on more data? So a few years ago, folks started to ask, how should I scale these two quantities with each other?

[54:53.037] Should I scale model parameters? Should I scale data? And we came up with all these very complicated power law curves that all look like this. They're very pretty. There's lots of colors. What you want to look out for is basically-- what you want to look out for is, if that curve is going down into the right, it suggests you should be scaling both data and parameters at the same time.

[55:16.140] If we were going straight down, that would mean just increase your training data. There's no need to increase your parameters. If it's going-- if it's flat, just going straight to the right, that means don't increase your data at all, just increase your parameters.

[55:31.347] But you see, it's going down into the right. That means you should scale data and parameters at the same time. And now you see this. You train a $1 trillion parameter model on $35 trillion tokens, and you get better quality. So our question was, OK, where does recurrence fit into this?

[55:48.200] And there are a couple-- so down into the right means you want to scale data in params-- there are a couple possibilities with recurrence. And so for example, you might conclude, you should never run a recurrence. It's better to just keep the same single recurrent model.

[56:05.380] You might conclude, you should do a ton of recurrence, or maybe only some recurrence to the bit. What we're showing here is, at least in these initial scaling laws, all of these curves are isometric, and ISO-param, ISO-FLOP. So each of these curves is a model.

[56:23.955] So on the left and the right, you have the same number of parameters. As you go down, as you change the colors, we are increasing the amount of flops that you use to train the model by increasing the amount of data. So here, we're varying data and varying the number of recurrences.

[56:40.650] What we find is that in both of these models, you see this down into the right trend again. So what this is suggesting is that for these fixed parameter training things, as you increase the amount of data, you should actually also be increasing the amount of recurrences that you have.

[57:00.290] We find that these recurrences follow some pretty classic power laws. So you can actually start to predict. You can get these scaling laws to start to predict quality, as you scale, recurrences and your tokens jointly. Yeah. For a fixed model size [INAUDIBLE] recurrence.

[57:18.650] What about jointly [INAUDIBLE] scaling [INAUDIBLE]? Yeah. So we have this really complex 3D figure that showed recurrences, and data, and parameters. And it pointed also whatever down into the right, and down that way at the same time. So if you believe that figure, it suggests you should be scaling all three together.

[57:44.930] But that figure was just really hard to look at, because it was 3D and weird. So these power laws suggest, when you're increasing data you should be increasing recurrence. And then you have other power laws that suggest, when you're increasing data you should be increasing parameters.

[58:02.090] So obviously, you should increase-- well, it suggests that you should increase all three of them if you can. But one piece here is that if you're going to fix your model size and you're going to increase the amount of data, you should also be increasing the recurrence, which is interesting because as far as I know, all of our models today have no recurrence in them.

[58:23.080] So they're all at the very left of these curves. And they all have a ton of data, which suggests that there might be something slightly better that we could be doing when training these models. And here's just that experiment in another way. So on the orange curve, you have-- so here, we fixed the model size.

[58:46.680] The orange curve is a fixed depth model. So this is like a traditional transformer model. The blue curve is when you fix the flop budget, where do you hit on the curve for a looping model? So here, the orange and blue dots have been trained with the same number of flops, but a different amount of data, but they're the same size.

[59:11.590] When you get to that number of flops by increasing recurrences as well as-- and not just increasing data, you start to get smaller validation losses, which again suggests it might be the case that we should be looping all of our big pre-training runs. So that's Parcae.

[59:32.630] If I take a little step back and go back to the big takeaway of the talk, I think hopefully, I've given you a little sense today of if you understand the inference of these models, if you understand the GPU kernels, you understand all the pieces that goes into it.

[59:50.290] You can really start to enable full stack innovation and machine learning algorithms. So whether that's through a new routing algorithm that lets you serve more traffic serve traffic in a different way. Or new kernels that allow you to run part of your system way faster.

[01:00:04.740] Or new architectures that say, if you have a lot fewer parameters, you can fit them in a subset of your GPUs in a different way, reduce the amount of communication, these are all different pieces of that question of that research problem that we're seeing today.

[01:00:23.520] And yeah, hopefully I've inspired at least one of you in this room to go take a deeper look at some of that. So with that, thanks. Happy to take a few questions. [APPLAUSE] We have about five, 10 minutes for questions. So if you have a question, raise your hand.

[01:00:46.000] Parcae, are you training from scratch on the loop? I guess I was wondering if you could take a picture of [INAUDIBLE]. Yeah. Great question. So the question was, with Parcae, are we training from scratch? Is there anything you can do with pre-trained models?

[01:01:04.560] So there was a really troll blog post from someone a few months ago where it was like, hey, I won some leaderboard competition without training a single thing. And what he did was he actually looped a two or three layers in a Quinn model, and just saw that on some math things it started having higher quality.

[01:01:25.240] So we have a little bit of work trying to look into this that maybe coming out soon. But there could be some models where if you do a little bit of looping just to the pre-trained model, you can get a higher quality thing, which is really weird. It disturbs me.

[01:01:39.620] I don't know why that would possibly be the case. But yeah, we'll be-- we're quite interested in this. I think we'll be looking at it and hopefully, if I can convince Hayden, he'll be staring at the activations-- at the actual weights to figure out why when you loop it, it gets better.

[01:01:58.450] Here's just a follow up on that. So you talked about compute optimality for the loop models, can you speak about the inference implications and the memory and how that can make you go faster? Yeah. So one of the reasons that I was personally very excited in these loop things is that, one of the big bottlenecks to serving inference efficiently actually ends up being GPU memory.

[01:02:20.010] So if you have fewer parameters, you can fit, for example, more KV Cache, or you can do less communication because you need to split your model against fewer GPUs and things like that. So there's actually a lot of flexibility that a smaller model will get you.

[01:02:36.810] I also had this dream that if you could make the recurrent block small enough, you could actually write a little Megakernel to just do that recurrent in a little very fast Megakernel loop. So far, we haven't been able to make those blocks small enough. But I think it's quite interesting.

[01:02:52.930] Certainly, with the next generation of the LPU, the Grok chips that are coming with NVIDIA things. Those have 250 megabytes of memory or something like that. So the thing that you'll be able to fit into them is very, very small. But maybe you can design something that will actually fit into them, and then you can just keep your weights in memory

[01:03:11.500] the whole time and just run your activations through as quickly as you can. So there are non-linear benefits that you can get if you can cross some of these thresholds that I'm hoping that we'll be able to get to pretty soon. Yeah, OK. [INAUDIBLE] I'm curious.

[01:03:30.560] I guess the trade offs are that it's always strictly more optimal. [INAUDIBLE] Great. So the question is, what are the trade offs for my kernels? The trade offs are people's blood, sweat, and tears. So Megakernels, turns out they're very, very labor intensive to write.

[01:03:48.580] So to give you some context, a full talented kernel engineer over the course of a year, will probably be able to write Megakernels for one hardware for two or three models for batch sizes 1 to 16. Go batch size 17, he was like nope, start over. Got to go again.

[01:04:11.288] So they're very, very challenging to write. And together, we're trying to put together some compilers that can automate some of that process. But I'd say, it's a very challenging thing to do. I think the basic Megakernel idea has gone in peaks and troughs over the last few decades when it comes to GPU programming.

[01:04:31.940] But yeah, so if you can do it, it will go super fast. You will never be able to go faster, but it just takes a lot of energy and a lot of effort. Cool. Maybe I can ask a question. So can we talk a little bit more about co-design? And in particular, you mentioned all these new hardware like Grok and Cerebras on the inference side.

[01:04:57.190] So if you're designing a model and that's going to be the serving platform, how should you be changing your architecture? Yeah, I think there's a couple of things that you should look at. So one is, you are going to be most constrained by memory first. So if you know that you're going to be taking a model and serving it a particular Cerebras chip,

[01:05:19.160] you want to go look at the Cerebras wafer, and figure out how much memory you have, and then size your model so that it can fit there with enough KV Cache or whatever to spare. If you look at carefully, at the Chinese models that are coming out, they've started making some interesting choices that suggest they might be starting to think about the Huawei chips that are coming out.

[01:05:41.110] You'll see quantization choices that people make. So if you have a model that you're intending to serve on NVIDIA GPUs, for example, NVIDIA's new Nemotron model that they released, you will train that model in NVFP4. This is a FP4 format that is proprietary to NVIDIA chips.

[01:05:58.400] If you're not going to run it on NVIDIA chips, if you're AMD, then you're going to run this other format called MXFP4. They each have their pros and cons. You'll make these subtle choices based on the hardware that you're choosing. I think there was a question over there.

[01:06:17.360] I was wondering if it's ever-- if you just care about compute optimal training, is it ever optimal to loop as opposed to just adding more parameters, or is it mainly like a trick to reduce inference cost? Yeah. So the trick with compute optimal is it is, usually, like given a flop budget-- --repeat the question.

[01:06:35.220] Oh yeah. Sorry. Yeah, the question was for Parcae, would you ever choose to loop instead of increasing parameters? And so the trick with compute optimal is always given some flop budget, figure out what you want to hit. It's almost a little bit contrived in that sense, because if you want a higher quality model, you should just increase your FLOPs budget.

[01:06:56.100] And if you decided on your model size, just train longer. Or if you're restricted by your model size, then loop longer. Or if you run out of data, then pick the model size that you think will be as overtrained-- as well trained as you can for that size. So I think there are choices.

[01:07:17.200] And of course, you make all these choices in the context of, do I think it'll get picked up? How am I going to serve it? If you're going to release the open source, what is the size of model that people can serve like on your laptop today? So I think all these choices go into making a choice.

[01:07:34.180] All these things go into making a choice of how big a model you choose to train. I think if you just make the model bigger and train it on more data, it's always going to get better. But I think it really depends on those design points. Maybe another question about co-design.

[01:07:56.955] So you mentioned at the beginning different use cases like agentic coding versus let's say batch processing of data. So what are the most dramatic differences in terms of optimal architectures that you see across different use cases? And at the end of the day, of course model developers has to pick one and try to not be reasonable on many use cases.

[01:08:23.010] Yeah. That's a great question. So I think one of the big differences-- so when you have these agentic looped workflows, one of the things that matters a lot is that you want to keep your KV Cache as hot as possible. So if you're doing a big batch processing thing where you only see each document once and then you translate it, the KV cache doesn't necessarily matter as much.

[01:08:47.220] If you look at something like the DeepSeek MLA attention, that is a radical compression of the KV cache compared to what you would have for another model. Or if you have the model that can process its KV Cache in FPA or FP4, those are pretty big departures in terms of the size of the KV Cache that if you are sensitive to an agentic workflow you would look at.

[01:09:10.859] Then of course, the biggest one is like causal attention or non-causal attention. So if you're just doing a big batch processing workflows. Like for the longest time, Google was just using Bert models. I think probably still uses Bert models on search. And that's because you don't really need to be generating a bunch of tokens on the other end.

[01:09:29.760] So you just do that big bidirectional attention once, you get your vector out, then you stick that in database, do whatever you will with it. Whereas the chat workflows, those processing, there's always going to be this decode portion of it. I think there have been intermediate things like T5 was at some point a choice that people made

[01:09:53.510] to do some bidirectional processing, and then also some generation. OK, maybe one last question. Oh, yeah. [INAUDIBLE], it was about using everything into one kernel, [INAUDIBLE] but what you were talking about before. So I was just wondering, how does that [INAUDIBLE] work a communication across multiple computers are scaling the cost of [INAUDIBLE] that.

[01:10:26.270] Yeah, great question. So the question is about, how does Megakernel work when you have multiple GPUs communication in the loop? We had some very early preliminary work about this. So it turns out you can also fuse the NCCL calls into the Megakernel if you set it up correctly.

[01:10:44.270] I think we haven't found a really great killer use case for that yet, where sometimes you're just bound by the latency of the NCCL call itself. So these are also pieces of things that you can fuse. When DeepSeek 4 came out, the DeepSeek 4s released a Megakernel for the mixture of experts inference layer that can run just for that where they actually did fuse some of those

[01:11:06.630] communication. So I think what we are starting to see, we're starting to see more of is, as you get to more of these models, you'll have a little Megakernel for a part for the computation, but you won't necessarily have a Megakernel for the whole model, unless of course, you pay the blood, sweat, and tears price and then really, really get the whole thing going.

[01:11:28.790] OK, I think that's all the time we have. Let's thank, Dan again. [APPLAUSE] Thanks so much for having me.
