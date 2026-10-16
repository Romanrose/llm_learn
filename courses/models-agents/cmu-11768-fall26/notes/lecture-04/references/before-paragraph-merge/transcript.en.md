# CMU 11-768 Fall 2026 · Lecture 4 · Agent Capabilities 3: Skills and Memory

- 视频：[官方视频](https://www.youtube.com/watch?v=6zigF2a-2Pw&list=PLSN0qpDfUvTM&index=4)
- 字幕：en-orig · auto captions
- 处理：连续字幕合并为自然段；每段保留首条字幕的起始时间戳
- 状态：原语言字幕稿，待校对

---

## 正文

[00:01.520] Okay, welcome back everyone. >> So, um the first assignment is out and uh as Graham said, we we have credits available for you to to work on it for those of you who are enrolled in the class. Do you folks have any logistic questions? Cool. Okay. So we talked in the last lecture about how agents can uh choose what to retain within their context window as a way of you know

[00:28.960] storing information within a task and using that to um to determine what's important to do better within the task. So a big part of today is going to be about how can agents go beyond the context window and store information across tasks in external stores um that will be useful for them to improve performance on tasks in the future. And this is going to be skill induction. Um,

[00:56.719] and uh, we'll build on some some work that was done in the past on memory systems for agents. Um, and show how to apply those to to agents. But there's also another view on skills. And skills are a way for people to write instructions for an agent that can encode kind of like best practices or the knowledge that you have about how a task should be done. And these are

[01:20.560] actually going to be complimentary to each other. Um so we'll cover it just a small amount in this lecture but um you can imagine a system that um is sort of having a human in the loop um that's relying on the agent to uh propose some potential best practices from the experiences that it has a person edit those and goes back and forth or vice versa like you know having a skill and

[01:45.280] instruction that's written by a person be refined by the agent based on experience. So yeah, it's a lot of different viewpoints, but hopefully by the end of the lecture, you'll see how they can all sort of fit together. So let's just start off with some motivation about why you might want to remember things from one task to another. So say that we have an agent

[02:09.039] that's carrying out tasks in a website like a shopping site and you might give it a task like add Sony headphones to my wish list. So when we cover guey agents, you'll we'll get into the details of, you know, the representation space, the action space for how a system like this works. But at a high level, it's going to be producing actions like um uh

[02:33.599] navigating to the store website, finding the search box for it, typing some text in that search box, and then clicking search. And that's going to be the part that like searches for the headphones, right? And then we'll do something with them. We'll find the ones that match the request the user had and put them into our wish list.

[02:51.840] We might have another task that we carry out in the future like find the wireless keyboard price range. And if we're doing that on the same site, a lot of the actions are going to be reused, right? We'll go to the store, we'll find the search box, we'll search for the different product but in a similar way and then we'll do something different with it like you know getting the prices

[03:11.519] and reporting those back to the user. But if it's difficult for the agent to figure out how to do this search, once it knows how to do it, it should be able to reuse that knowledge in the future to be more effective on future tasks. So a lot of structure recurs and today is going to be about how can we represent this shared structure. So for example, is it best to just uh keep kind

[03:38.640] of the raw actions that the agent produced when it was carrying out this shared subtask or is it better to try to abstract it into for example a code function which could be run as a blackbox or maybe tested or even like hierarchically call other functions.

[03:57.120] We'll also be interested in how can the agent like determine which parts of a task should be reused in the future. And um as we're you know any time we have a memory that we're building up from experience, there's questions about um how do we grow that memory? Do we are we always adding to it? What happens if we get some conflicting information or

[04:22.400] we find a better way to do something? We might want to make edits to it. we might want to delete things if they no longer seem to apply. So, how can we um kind of manage the life cycle of these skills um and these subtask representations that are learned? [snorts] So, I'd say there's three general ways that we can get agents to update. So, the first one we covered in the last

[04:47.759] lecture. It's um just what you maintain in the context window of the model. So this is um you know in the standard React style way. It's the history of the past observations and actions that you've taken, messages you've gotten from the user, feedback from the environment, and you need to you need to choose like what to retain given kind of the limitations of the context window

[05:10.560] and the model's ability to use that. So uh we talked a lot about like compaction and methods for managing what's in that context window. Today we're going to be focusing on storing things outside of the context window. So even with like really long context windows that we have now of like a million tokens uh for um multiple for like carrying out multiple

[05:34.560] tasks with an agent um you're going to exceed that context window and you want to remember things from past tasks to help you on future ones. So if we are storing things outside of the window, um that's going to look something like a database um that needs to be managed um in some some way or um like a file system that the agent can access. And uh this lecture is going to be about

[05:59.759] methods for um putting things into those types of storage and um using them and updating them. And then the final way is going to be like actually making uh updates to the weights of the model. Right? So this looks more like standard supervised fine-tuning or reinforcement learning. We'll cover that in a few lectures later on. But each of these has

[06:21.600] like pros and cons. So um I think like a main pro of using external artifacts is that they're like they can be ported across models, right? So if you um have a description of the way to search for a product um that could be used by any one of a number of different models um within an agent framework. Whereas if you're actually making updates to the weights of the model that's just an

[06:49.120] update for that specific model and it doesn't transfer to others. So external artifacts are also more inspectable by people. Um, so you could write down best practices or how to search on a site. The agent can use that. The agent could also propose, you know, kind of text for that and you could look at it and make changes to it. So there's it's easier to

[07:11.199] kind of like have an interface between the person and the system if your um method of updating, if your method of remembering is interpretable. Any questions about this? How many folks have uh have used skills in their interactions with the coding agent? Like how many of you Okay, so most folks have. How many of you are are writing the skill yourself?

[07:36.880] Okay, so maybe about half the folks who are using skills. How many of you have uh gotten an agent to write a skill for you? Okay, so a lot of folks actually have. Yeah. What are some things that what how what's your experience been for the agent writing the skills? How often have you been able to use it just right out of the box? The thing that the agent constructs

[07:59.680] anyone have any spectacular failure cases or spectacular successes? So just repeating that for the recording like sometimes the models will write too much in the skill like they'll kind of overinfer the what should be done and then when that's handed off to another model it will kind of follow it to the letter and do a lot more than you actually wanted it to.

[08:22.800] >> Any other examples from folks? >> Cool. Oh yeah, go ahead. I mean in cases when you're like trying to like a production issue for like a particular system if you give it like three or four support and you tell it that look at how people have this issue in the past create a skill for yourself other agents could use to it in the same way >> and that's very >> oh nice

[08:52.959] >> okay cool yeah so instructing it to like get write the instructions for another agent it's good enough it's sort of like simulating what the agent would do. Yeah, that's interesting. I've sometimes found that the models are like pretty bad at kind of like simulating the theory of mind that you know another person or an agent would have when they

[09:10.160] like look at instructions, but they get a lot better when you prompt them to do that. Cool. Okay. Yeah. So, a few different like types of experience that we might want to retain for agents. So the first is like the episode and this is you know just the sequence of observations that you get from the environment from the user and the actions that are taken and this is

[09:36.240] sort of like the maximum fidelity right you're just you're retaining everything you have all the specifics of that particular environment and the particular instructions that the user gave also going to be like the most costly right it'll need the most tokens to represent and you probably don't need all of that right? Like uh just like when we're doing you know supervised

[09:58.240] learning we don't want to retain every detail we want to abstract to the things that matter to generalize um in the future. So we could also retain some facts like um some knowledge about the environment um or about the user and in the early work on memory systems uh a lot of it was focused on retaining facts. So like a user is interacting with an assistant and maybe gives some personal

[10:26.640] information like how old they are or where they live. The system can retain that in its memory and then use that fact to improve future interactions. If you've um used uh like Anthropic or Chatbt's uh memory systems, uh they're doing this basically, right? Like you can go into the settings, you can view the memory that they have about you and there's, you know, a text representation

[10:50.399] there from a model that's produced those facts um from your past interactions. Looks a little bit like compaction in some way. It's generated by an LLM. It gets stored in this external thing. And then the final one is more specific to agents. So it's about like how do you do part of a task um in a way that's abstracted from the details of the task.

[11:14.000] So like in the example we looked at before, how do you search for products on a particular website without maybe retaining the details of searching, you know, the particular product that you searched for? And so there's a lot of choices about how you would represent a skill. Is it just text? Is it kind of the actual actions that you took? Um or could it even be code?

[11:35.680] And of course, skills are only going to be useful if you're going to be doing the same subtask more than once. So we could think about like um memory and skills and the intersection between them. So memory is just something that we're saving from the agents interaction. So for example, what's a previous product that you purchased on a site? A skill would be reusable

[12:00.320] knowledge about how to act in an environment. um which could be represented in one of a variety of ways. Like it could be, you know, if you're releasing a um application um by pushing it to production, here's a checklist that you need to go through before you do that. So, a skill could be written by a person like in this example. But we could also have um a combination of

[12:24.720] memory and skills. So we could induce skills from the agents past experiences and store those um and then use those to hopefully do better in the future. So if the agent searched successfully for a product in the past um and uh yeah and if it was successful, if we think that it was successful, then we could pull out something that looks like a skill to

[12:45.680] guide the agent in the future. And we'll get a lot more concrete about what this looks like through the rest of the lecture. So we can think about skills as instructions where uh skills as instructions might be written by a person um for encoding their own you know preferences or might be organization policies like this is the way that we write and test code in this

[13:10.880] particular company. Um and human authored skills um we know where they came from. we have more maybe control over the quality but it takes you know a lot of time to write them and to maintain them. If we're learning skills then the agent is producing them. Um and this is helpful because we can do this in an automated way. Maybe we can have like a loop where we induce the skill.

[13:34.399] We try to use the skill to redo the same tasks. We see if things get better on a metric. Um, but it can be, you know, potentially noisy too and have, you know, especially if you're using the skills for some other agent like we talked about in those examples everybody gave, um, it could maybe have unintended consequences too.

[13:54.800] Okay, so let's talk first about uh, humanridden skills and um, the standards for these and the ways that they're used in incurrent agents. So probably a lot of it sounds like a lot of you have experience with this already. Uh so maybe you've been using these in the context of an example kind of like this.

[14:15.920] Uh there's this nice blog post from open hands that has guidance on using skills. Um for those of you who um who haven't used skills yet or if you you know like some suggestions on how to uh how to have best practices for creating and using skills. But they have this motivating motivating example of say that you find yourself like always giving similar instructions to a coding

[14:39.839] agent. Um so you um want the you want to check the code that has been written using one of a couple different llinters. You want to give type hints. You want to use a particular type of dock strings. And you want to apply piest to all the functions. So if you're always doing this, you could always type this guidance into the system. Um, but you know, a kind of natural and faster

[15:04.959] way to do this would be to just have the like store the guidance as a text file and then have the agent use that guidance um as an instruction. So you should reach for a skill when you want to do something repeatedly following kind of like a fixed specification. And the agent's going to choose how to interpret this specification in context, but the um general instruction is the same.

[15:31.680] And the way that this is implemented in the current standard for skills um which is called agent skills is just as a collection of files which the agent is able to read. And here's an example of of that. So if we are constructing a skill for Python review um we'll have a folder which has a structure like this. So skills have this standard structure where they'll

[15:58.399] have a skill.md file and you have to have that. Skill.md um is a markdown file that starts with um some YAML metadata. So you need to have a name for the skill and you need to have a short description uh which is going to give guidance to the language model about when the skill should be applied. And we'll see in a slide or two about how the model gets access to this

[16:22.959] information in the YAML header. And then um after the header you'll have a much more detailed description of um how the skill should be applied which would for example you know list um here are all the llinters that you should apply here's how testing should be done and so on. So you have to have skill.mmd. You also have a few other um folders which

[16:44.639] are optional but can contain some extra resources for the agent to use as it carries out the skill. So there's scripts which has executable code. So for example, if you had like a Python script that would run a llinter, you could put it in there and then describe it in this skill.md file. There's also references, which would be sort of like supplementary documentation that maybe

[17:07.760] you don't you you don't need to use it every time you use the skill. Um, but you'll have maybe a reference to that documentation in the skill file. The agent could load it as needed from the references folder. And then assets basically just has like, you know, additional templates or resources like if you're, you know, doing something that involves like Ginga and you need

[17:28.319] the agent to load that conditionally. So this can be a lot of information, right? And we um don't want to fill up the context window of the model um with all of the possible skills that it could use. So there's a mechanism called progressive disclosure which is going to just show relevant parts of skills to the agent as they're needed. So the first level is um the metadata in this

[17:56.320] YAML file. Uh so the name and the description and that's always going to be um shown to the model in the system prompt if the skill is loaded if it's available to the model to use. So you need to be kind of concise in this uh description. Um so that if you have a lot of skills you don't fill things up too much.

[18:19.039] There's the second level which is the rest of the text in the markdown file and um that'll be loaded conditionally if the model decides that the skill is relevant um and uh decides to read the rest of the file via a tool call. We'll see an example of that in a minute. And then the next level is sort of like all the resources in here which will also be

[18:41.919] loaded um using tool calls. So you kind of need to have enough information in the skill.md file for the model to be aware that it should look into these additional folders to get more resources um when it's carrying out the skill. Any questions about this and you'll implement this in assignment one or maybe some of you are already starting on implementing that.

[19:05.840] >> Yeah. are so high like what if that takes too much of that effect performance? >> Yeah. So if you have a lot of skills even if the skill metadata is pretty short could it affect performance? Yeah, it definitely can. Um so you want to keep the number of skills somewhat small and maybe just load them conditionally.

[19:36.320] um in one of the state-of-the-art agents, Hermes agent, I think the I'm not sure the number of skills, but like the total length of the skill descriptions in the system prompt is like 3,000 tokens. Um there's some papers that we'll see in a little bit that show that if you have too many skills, um it can make performance worse. Like adding in irrelevant skills

[19:56.559] can drop performance um because, you know, the context gets longer. The model might be distracted by things that are actually irrelevant. So yeah, you definitely need to be careful about the number of skills, but um I think it would be pretty rare to have like 10,000 or a thousand skills. Generally, it's, you know, smaller and you would maybe load skills as needed for like the

[20:16.640] software tasks that you're carrying out. >> Yeah. >> How sensitive are those triggers? >> Yeah, that's a great question. How sensitive are the triggers? So the the triggers will be tool calls that will be generated by the model. And so whether they get called or not is a function is totally dependent on the model. Um and you know the model's ability to predict

[20:43.039] that it should be triggered based on the past context and what it knows about the skill. So that you know depends on the model depends on the description you write and um that's why we need evaluations for this. Um and one of the papers that we'll look at takes a step in that direction.

[20:59.919] >> Yeah. like a standardized name. >> Yeah. Uh skill.md is a standardized name. So the the standard is called the um I think the agent skills standard and um you like models agents are trained to to use that agent frameworks are trained to load that. Um so yeah you um if you want to use an alternate format well first put it you know as close to this

[21:29.679] as you can but you could do you know if you have particular if you have particular um things that you want like in the references folder you could describe them in skill.md and like all this is just going to be instructions to the language model so it could be robust to other configurations also especially if you describe them.

[21:50.799] >> Yeah. Why are >> Yeah, why markdown? It it is a balance of machine and human readability, I think. >> Yeah, that's a great question. Could there be better formats than than skill.md? Yeah. Do you have things in mind? I think like um so uh I mean it's just like linear right um it's you can have hyperlinks which is good you can embed images too um >> yeah um but uh like it's difficult to

[22:36.799] you know represent things that are dynamic so like maybe you want to illustrate to the model like um different ways the data could be visualized um you know maybe that would be better with like a JavaScript interactive JavaScript application or something like that. Um, yeah, you could, you know, have that be sort of like a code file here that gets executed. Um, but and maybe like

[22:58.240] referenced in the markdown. Um, so I think like markdown is sort of the best attempt at having something that's general and like readable, but then you would rely on the language model to interpret other formats. >> I think in the scientific literature that uh Daniel's going to talk about, there's basically two ways. There's textual skills and programmatic skills

[23:18.960] and the textual skills appear in the markdown and the programmatic skills appear in the script. So it kind of it's pretty broad if you consider those. >> Yeah. Cool. >> Yeah. >> Does anyone do to not have to put it all in context? For example, if you're making an agent that modifies cloud infrastructure, you work at some big bank and have a billion

[23:42.000] things in AWS and it would be nice to be able to just ask the model to modify something, but then because it's a billion things, you can just have a billion tools for every small component available. Yes. >> So looks like something would do. Yeah, definitely in some of the research papers that so the question was like do people retrieve from large collections of skills. Um and yeah

[24:08.400] definitely in some of the research papers that we'll look at um they do that um either using you know just like a text embedding based retrieval or doing something that's more kind of like domain conditional like we know these skills apply to this site so when we're interacting with that site we'll load those skills. Yeah, I imagine production systems do this too, but um yeah, I

[24:30.799] don't have any references off the top of my head for that. Cool. Okay, so we'll uh just uh kind of quickly to show you how progressive disclosure works. Um we first need to give the model access to this level one, right? Let it know what skills are available. And you'll have a system prompt that looks something like this. This is just taken from Hermes

[24:53.120] agent which is sort of like a standard open- source um agent that is able to use and induce skills and you'll um kind of describe what skills are. Uh you'll tell the model about this skill view tool which it could use to read the rest of the markdown file and then you'll list out all the skills that you have.

[25:14.080] So there's just two skills here. Um, there's a code quality skill and a workflow skill. And that's just the YAML metadata from those skill files. So, um, the model is able to use tool calls to, you know, expand the rest of the skill. And here's what that might look like. So, it always has the index of skills in the system prompt, but it could choose to make a tool call to open

[25:41.039] the Python review skill. um if that seems relevant to you know the user asked for a review of some Python code and then it's going to like um you know get that markdown file insert it as a message to the system as an observation the result of that skill view tool. Um the system might choose to run something from the scripts directory um and then it'll get the result of running that

[26:06.720] script as an observation put it in the window um and might choose to you know like view additional files within that skill package. Okay. So yeah, we these questions that we had about like you know could additional skills hurt um are skills being triggered in the right place. Uh we answer questions like this by building evaluations and um the the work

[26:33.600] on this is a little bit um new. It's sort of ongoing but um a really great first effort in the space is called skills bench and what they do is they um collect a bunch of skills uh from uh various sources online. they actually get like 2 million skills. Um, and they'll also have people write tasks which seem like they could benefit from skills. Uh, and so they'll like get 400

[26:59.760] tasks and um those are going to be written independently from the skills, but they'll have the task annotators choose from this pool of skills ones that seem like they could apply to the tasks. And so you'll have kind of like a small set of curated skills. um and you'll supply those skills to an agent as it's trying to solve the task and they'll evaluate this on like um you

[27:23.679] know four different agent frameworks uh with I think like 18 models something like that and they'll just see like does having the skills um improve performance over not having the skills across all the tasks for a given agent framework and model combination right so this will evaluate you know it'll implicitly evaluate the skill quality but will be designed to evaluate is a model and

[27:50.480] framework able to you know use the skills appropriately and they're trying to choose the skills. So they have like a filter um which checks to see that for a small subset of models the performance on the tasks does improve when you give models access to the skills and then you're seeing if that's also true for kind of a wider set of frameworks and models.

[28:15.039] Yeah. Does the general setup make sense? Cool. So on average, you know, with this cur curated set of um skills, uh the average pass rates on these tasks using like humanridden verification criteria does increase. And so you can see like the solid bars to the shaded bars across a bunch of different models um and frameworks. Um but actually uh ski like

[28:44.559] tasks that require fewer skills to solve benefit more from having the skills available than ones that require more skills. Um and so this is partly a difficulty thing but also partly that the models might be getting distracted by having more skills available. And you could imagine that it's getting much worse with like a much larger number of skills. Um we'll see some more evidence

[29:08.480] for that later on in the lecture. And actually skills still hurt on a number of the tasks for particular model types. Um so the model might be using the skill inappropriately which could actually make it do the task in a way different than what the person specified. So this kind of motivates the importance of like checking to see if the skills that you wrote are actually

[29:31.440] making your outputs better. So skills can come from, you know, a bunch of different sources. They could be bundled with the harness. Um, they could be written by a person. Um, and a lot of you have done this, it sounds like, and you then, you know, kind of install it in a in a way that's specified by the framework that you're using, but they can also be created by

[29:55.120] the agent. And, um, Hermes has a skill manage tool. um open hands as a skill creator uh command that help work you through the process of creating a skill. And when you're creating a skill, I think it's really important to base that skill on some prior interactions that you've had rather than trying to just do it sort of a priori. Um and actually

[30:19.520] there's some results in the skills bench paper that show that models when they're tasked to create a skill by themselves just based on a task description, they're really bad at it. and it actually makes performance worse. So, as a person, you're probably better because you kind of like know the way that you want it to be done, but it's generally best to base it on, you know, past

[30:38.720] things that you've done because when you're doing a task, it'll reveal some things about the way you want it to be done that you might not know in advance. So there's a nice case study of this um from the open hands blog post on how do you like so you have this code review skill that you've created. How do you check and see if it's working and then improve it if necessary.

[31:01.360] So this is focused on like reviewing poll requests and what what you could do is like um after the review is produced by the agent then a person is going to go through the poll request and look at each of those review comments and either address them or not. And you can apply a modelbased judge after that and count up how many of these were like actually

[31:24.240] used by the person which will give you a sense of how good the pull request was. And you can like um do this over a large number of pull requests that were created and then reviewed by the agent using this skill. And um if you do this over um you know like hundreds or thousands of examples, you'll get a lot of evidence about what's working and what's not, you can summarize all of

[31:49.679] that with a reasoning model um and use that to like for example identify that it's not helpful to um you know produce code that ignores the repo conventions. people did like incorporate those changes quite a bit. And then you could like have the model propose some updates to the skill file that will make the you know reviews produced by the system more

[32:14.159] likely to be incorporated by the person. Cool. Any questions before we move on? Okay. So next we'll talk about how do we get models to automatically remember things from their past experience and then we'll use that to like build on um to talk about inducing skills from experience.

[32:40.480] So this is this is an old paper. This is from 2023 um but it was pretty influential. Um and it's uh it's one of the first papers it's called MEMGPT. It's one of the first papers to uh [snorts] introduce a way that you can manage memory outside of the context window of a language model. So this is like a really a systems inspired paper. I think we talked about a couple lectures ago

[33:07.360] about you know kind of having like memory hierarchies like you know something that is fast to access which for the language model is the context window and then something that's like larger but but slower and in this setting that would be like an external store of of facts and back when this paper was written uh a few years ago context windows were even shorter like

[33:29.679] you know 8,000 tokens um so this sort of approach was really well motivated even for just interacting with like an assistant system. Um nowadays you know our context windows are larger but what you want to store in them is also much larger. So this sort of approach is pretty well motivated for agents too.

[33:48.399] But the basic idea here is that you're going to have like a um you'll have you know the system instructions which don't get updated. you'll have a working context um which is going to uh pull things from an external memory um and also you'll be storing things to this external memory and those reads and writes are going to be controlled by tool calls from the model

[34:15.919] and um you'll also you know have like a separate storage for the actual messages that the system received um but that's going to be controlled in a pretty similar way to this uh this memory over fax So, what this actually looks like, sorry it's a little bit hard to read with the brightness in here, but like if you um you might uh have an interaction with

[34:35.760] the model where the user like mentions six flags and um the system could produce a tool call that searches within this storage for past mentions of six flags from its past interactions. It'll take those and it'll put them into this like working context. Um and then the model um this working context is stored within the context window of the language model. So the model will be

[34:58.880] able to use those as it outputs its response. But it's important to be able to do more than just like add to memory because for example like um maybe you're talking to the system about your job. you say I work at X, but then if you change jobs later on, you want the system to be able to like use the latest information.

[35:26.000] And um this paper called me zero uh introduces a way for memories to be updated as well. Um so the way that this works is you'll have like messages coming in and um each time you get a message, you'll apply a language model to extract some memories from it. um some like potential facts that you might want to store or update and you'll have an external uh database store um and

[35:54.240] you'll try to check and see do I have anything in that database store that's relevant to these um facts that I pulled out of these messages. So you'll retrieve the top K and to do this you'll use like an embedding based retriever model like you know the ones we talked about a little bit ago. um you'll pull out similar facts like um six flags for example or like um I work at X and

[36:18.560] you'll apply a language model to check for all of these extracted memories from these latest messages um do they um are they present in these similar retrieved memories? If they're not present then we should potentially add them in. um if they are an update to something that's there, we should replace what's stored for that with the new thing. If it

[36:44.880] negates something that's already there, like for example, you say, "I work at X," but then later on you say, "I got laid off," you might want to just delete that fact rather than um than updating it. Um or if it's not relevant at all, you would just ignore it.

[37:01.280] And um I'll refer you to details or for the paper for for details about this um because the details also change with with agentive systems but I think the idea that um it's useful to be able to like update knowledge as well if you have conflicts is potentially pretty useful.

[37:18.880] So, um, does anybody remember something from the lecture on context management that had a similar goal to this being able to update or delete memory? Yeah. Uh, hashing. >> Yeah. Yeah. Basically, does anybody remember the specific paper? Yeah. Yeah, it's hashing in the sense that there we had like key values and queries, right? Um and we were like storing values which were vectors. Um

[37:52.800] here we're storing like text um as facts. Yeah. So the Delta paper actually did this, right? like um linear attention is only able to append um values to your um what's effectively your memory but Delta um uh like effectively retrieves um things that are stored for particular queries and then changes them changes the vectors that are stored for for them

[38:24.880] and that helps improve performance. So this is sort of like a textbased analog of that that has a similar goal. Yeah, you could also think about like um for the third type of learning for updating the weights of a model, it's potentially helpful there to be able to forget stuff also. Um especially if you have kind of like conflicting knowledge and and people are starting to develop

[38:47.440] some approaches for that like unlearning um is one way to do it. Okay, so those are some foundational papers about memory um that were developed for assistance for agents. Um feedback on trajectories can be really useful. So this paper called reflection was um a really impactful it's a really uh it's a really pretty simple but effective um the way to get agents to use feedback and

[39:20.480] potentially do better. So, it's definitely worth knowing about. It's a good thing to implement if you're working on a project that might want an agent to be able to benefit from its past experiences. Um, and the way it works is we're trying to improve the performance of an agent given multiple attempts on a particular task. So, say that you're asking the agent to like um,

[39:42.720] you know, search for a product on a website. It makes one attempt at it. um it says that it's finished and you're able to get some feedback about whether it was likely correct or not. So that could come from like a person looking at it. It could come from applying a model as a judge. Um but given that feedback, you'll want the model to try again and try to do better.

[40:06.480] And what this paper does is show that natural language feedback um on the attempt can be a really helpful thing for the model to condition on in its second attempt. So like if it's trying to answer this question about what was a particular series of battles, it might just mention one particular battle and then the feedback that's given um generated by a language model based on

[40:28.960] knowing this is incorrect and looking at the question and the answer might be um you gave just a single battle rather than a series. So as you can imagine this would be really helpful feedback for the model to condition on as it you know does another attempt at this task and it can get it correct. Um and the paper shows that you know conditioning on this natural language description of

[40:50.560] what went wrong can be really helpful. So we can generalize this also to um the agent improving as it does different tasks. Right? This is improving on the same task. But you could imagine um feedback might be generally helpful to improve performance on similar tasks as long as the feedback's like sufficiently general.

[41:15.280] And the final way that we can like um have agents uh improve or you know kind of the final foundational thing for helping agents improve um is remembering trajectories uh like entire trajectories, entire episodes that they've done in the past and using that to shape what they do on future tasks.

[41:34.240] There is a bunch of papers that have done this. We have some links to them at the bottom of this slide. Um, but the key thing in all of them is you'll have some collection of like training tasks and those tasks could be like a collection of demonstrations or they could be produced by the agent as it's carrying out tasks one at a time. Um, and you'll pull all of those tasks

[41:54.560] together. Maybe you'll additionally like um generate some text that describes uh feedback from them sort of like reflection did on the last slide. And you'll have that pool of experiences. And then when you get a new task um that comes in, you'll retrieve from this uh set of trajectories and um maybe generated text about them to find something that's relevant for the task

[42:18.640] that you're carrying out. You'll put it in the context window of your model and it'll generally help you to do better. Um so this is sort of like rag for agents, right? Um and uh it's pretty effective. Any questions about this? Yeah. >> What do you mean by trajectory in this case is like sequence of calls.

[42:42.800] >> Yeah. Yeah. So a trajectory generally for an agent is the sequence of um like messages that it gets from the environment or the user. So the observations um the actions that it takes like the tool calls and um and uh potentially also you know the chains of thought that it produces. So one way to think about it is basically just like all the sequence of um of uh messages um

[43:07.680] in the context window of the model >> and you retrieve it by image differently. You can do this regular embedding retrieval or compare to process sequences and do some set comparison. >> Yeah. What are the different ways that you could do retrieval? So typically you want the model to you're giving the model the description of a new task that it should carry out. So you have just

[43:33.040] that text description and you'll embed that um with an embedding model and you'll retrieve um based on the descriptions of other tasks that each have like a trajectory associated with them and maybe you'll also constrain that to be like we'll just retrieve the tasks for this particular domain that we're working in. Um yeah, good question. Any other questions about this

[43:57.359] approach? Generally, this is sort of like a whole class of approaches. Um there's different ways to instantiate it. Um the details like how do you build up the experiences? How do you do the retrieval? Um but just want to kind of give you a sense that if we have past successful trajectories and we show those as examples to the agent, it can help it to do better.

[44:22.240] Okay. So with that we kind of have the foundation for talking about um actually inducing skills. Um so we can think about skills as being like parts of a task that are reusable across different tasks. So at the very beginning we talked about like searching for a product and that might look something like we tell the agent show me results for this particular query and

[44:50.720] the agent might produce a chain of thought like this and then it might produce these particular actions that actually interact with the web page like um uh clicking on this element identified by this particular ID which is the search box typing a query in there and and clicking on another element which is like the actual button to search.

[45:13.359] And this uh chunk of a task might be reused on future tasks. Like if I say what is the price range for um this particular item, it might need to do these same exact steps again as well as some additional ones afterwards. And so we can think of a skill as being um a specific like reused part of the task.

[45:38.640] Is this a good way to represent a skill? Can anybody think of any issues with this? >> Yeah. just >> Yeah, that's right. Yeah. So, like if the element ids on the page change, the skill will break. And you know, there's a number of ways that that could happen.

[46:07.839] Like, you know, maybe the elements are maybe it's the same page, but things are just numbered differently. You can make some changes to the action space to deal with that. I think JY will talk about that in his lecture. But like if we go to a different website that has like a different search interface um it's going to break and we'll see some examples of that later on.

[46:31.440] Yeah. So we'll generally compare as Graham said text versus code as ways to represent skills. I want to briefly highlight some uh really cool papers um from the past that I think kind of like lay a foundation for skill induction um for learning skills from experience. Uh, one is called um Voyager and um they're controlling an agent in Minecraft. Um, and they're using uh code as a way to

[46:58.960] control the agent where the code functions um implement things like um crafting a particular item or combating a zombie. And representing these like subtasks as functions allows functions to call each other. So that as the agent like learns functions for simple things, it can then like compose them calling them in other functions and you can carry out increasingly complex tasks.

[47:26.400] There's also a line of work um from the program induction community um that that does this. I think a really nice representative of this is um uh work called dreamcoder and a few papers that built on it. And there you're um sort of uh you have basically like grammarss over things that you're constructing um like objects um and you uh like have uh some examples of complete objects which

[47:53.119] are constructed using like very low-level functions and you search for recurrent patterns in that you find patterns that can be abstracted into functions and you do that repeatedly and you're sort of like compressing the programs that construct these objects.

[48:07.680] And then there's also some follow-ups to this that uh integrate like large language models, Python code, and uh natural language descriptions too. And some of the same ideas in those papers are also useful for agents that are um using language models to interact with the world. A typical way that we'll evaluate systems for inducing and using skills is an online learning setting. So

[48:36.000] when you're interacting with um an agent, you are maybe having it carry out a bunch of tasks in succession and some of those tasks are going to be similar to each other. You want the system to be able to learn from your interactions with it and then be able to do better in the future, right? So um this is an online learning setting where we'll have tasks come in one at a time. So for

[48:58.800] example, like you might say, add a Sony Bluetooth headphone to my wish list. And we'll be building up a memory of skills um incrementally as we solve those tasks. So um there will be an induction step that we'll talk about in a slide or two. And that induction step will create a skill like search for a product and add a product to the wish list that

[49:22.240] are useful for solving this particular task. And um you know maybe we have another one like this task here and we can apply those skills on future tasks like this task might also involve searching for a product and hopefully we'll do better on that task given that we had this skill induced from the previous task and so on. So what we're interested in

[49:49.119] is if we can measure success on each of these tasks, is our success rate like getting better and better? Are we able to solve increasingly complex tasks um as we're learning from experience and building up um uh representations of the ways to do these simpler tasks? Any questions about this setting?

[50:11.760] Okay, cool. So the papers that we'll look at for the rest of the lecture look at sort of different parts of this space of um uh learning skills from experience having this library and ask questions about what should we do with the skills like after we've um induced them. So there's generally like a learning step where we'll have these uh tasks coming in.

[50:37.440] We'll try to get a skill out of them. will decide whether to store that skill um in the memory that we're building up over time. There's um the step of like actually using this memory of skills to potentially improve performance on the tasks that we're carrying out. And then finally, we might want to, you know, if we're getting too many skills, we might

[51:00.000] want to try to simplify those, like delete the ones that aren't being used, or if they're too specific, we might want to make them more general. um or like consolidate and merge multiple things together. [clears throat] We'll go a little bit deeper into one paper um that I think is pretty representative of ways for inducing skills. Uh it was also done here at CMU

[51:24.880] as work led by Zora Wong who will be giving a guest lecture on some other topics a little bit later on in the course. Um but this paper's called agent workflow memory and um the way it works is it we applied it to web tasks. Uh this is work with with Graham also um and me and uh we applied this to web tasks and you have a query like this and you know tell me the number of reviews

[51:51.839] that our store received so far and when the agent's carrying this out these are the actual tool calls that it'll produce. So we have this sequence of tool calls and we want to try to identify which parts of this might be potentially reusable in the future and you can probably guess how we do this. We ask a language model to take a look at the sequence of tool calls and

[52:15.760] identify ones that seem like they might be useful on future tasks. And we'll have the model output what we call workflows um which are sort of like a textbased representation of skills text and actions. And a workflow will have like a description of the subtask like searching for a particular item.

[52:37.200] And then um it'll have the sequence of actions that you use to do that. And we're having the model make this a little bit more general so that it could apply to like searching for other terms. So we have it use like create a template that can abstract out some parts of the um initial action sequence. You might be thinking like this is starting to look

[53:00.480] like code, right? That's true. Um and a little bit later on we'll compare code to this also and show how that can be better in some ways but also uh make things a little bit more uh fragile. A pretty important part of this is we'll um apply a judge model to this trajectory to decide um have the judge predict whether the trajectory seem to be correct or not. And we'll use that to

[53:28.400] determine whether we should actually add the workflows that were induced to the memory. Um because we don't want to be um remembering things that were incorrect because those might steer the model wrong in the future. >> Any questions about this? Okay. And so the way that we'll um give the model access to these uh collection of workflows um is just by sticking them in

[53:59.760] the context window of the model. So this looks a lot like you know this agent skill standard. Um you have choices about whether you show everything or whether you show just you know kind of the text description. um and what you do there could depend on how many skills you have and you know the context length of the model.

[54:20.000] So um for the sake of time I I'll skip over this induction prompt but we do find that um having this memory of like past uh subtasks um can help to improve the performance of the agent as it's learning online. So on the x-axis here we have like um different tasks in a fixed ordering from this benchmark involving interacting with like a map tool and the blue line here is the

[54:45.760] baseline agent that doesn't have a memory that sort of converges to around you know like 10% accuracy on these tasks and the labels here are the tasks that are being solved by the agent correctly. Um and then this black line which adds in this memory of um subtasks improves pretty substantially and it's able to um you know this gap emerges between the two but it's also able to

[55:09.200] carry out these like increasingly complex tasks eventually doing things like you know finding a hotel near this location showing me the walking path um that the baseline agent just isn't able to do. So this is using, you know, sort of this mix of text and example actions to represent skills.

[55:33.599] But we could also consider using code, right? And both of these are implementations of a search product um function. And if we're using just this text and examples, this is going to be in the context window of the model. and then it's going to be needing to produce these tool calls um in a new context, right? As it tries to carry out the same subtask. So, it's flexible like the

[55:59.760] model could choose to insert a particular search term to search for a different product. If the website has changed and we no longer have like this particular um element for the search box, then the agent could choose to use the correct one instead. Um, but it also means that the agent needs to like actually produce all of those tool calls itself. If we're using code, the agent

[56:25.760] could actually just call this function as a tool, right? If it passes in the right arguments and if the functions correct, then it doesn't have to do anything. It doesn't have to produce all of those low-level actions itself. Um, the tool will just do that as it executes in the environment. Can anybody think of uh some pros and cons of using a function like this as a representation

[56:45.920] for a skill? Any cons? >> It's very rigid. >> Yeah, it is very rigid. So like um the model will need to the model calling this tool will do exactly these three steps and there's no room to to deviate from it. Um yes that's a main call that's a main like con to it but we also get a lot of the pros of using code right so like we can nest functions it

[57:22.799] can be hierarchical we can actually like generate test cases for that specific function too independent from the entire trajectory that it's executed in. And we can do things like you know refactoring also. So uh Zora has another paper um called inducing programmatic skills or agent skill induction which um which do this and it looks pretty similar to the

[57:47.839] approach we were using to induce these textual workflows. So you have a trajectory like this with these tool calls and we'll have the language model um we'll we'll just use the fact that language models are also good at generating code and we'll um prompt the model to generate functions which abstract a lot of the um uh behaviors in this trajectory and these are real

[58:13.760] examples. So the language model will write this search reviews function and um a doc string for it and then you know it has these low-level tool calls as um lines in the function. This other one for open marketing reviews but we'll also have it generate sort of a rewrite of this original trajectory that uses those tools. So a really nice thing about um code is that we can test it by

[58:37.040] executing it. So instead of applying the judge to the original trajectory like we did before, we can have the language model. Well, we can execute this generated abstracted code and then apply the judge to the end result that you get from that. And if that appears to be correct, that's sort of like a stronger indicator that the skills, these code skills that you induced are also

[58:59.280] correct. And if they are, then we put them in the memory and they become usable to the language model just as tools. So this is a way of like building up a tool library that the model's able to use on future examples and um we show that it also you know improves performance.

[59:19.680] Any questions about that? Yeah. So a nice thing about um code skills is that they allow testing just of the skill by itself. Um there's this nice paper called skillw weaver which does this. Um, so this is sort of some pseudo code for the uh the loop that I just showed you where you have a task, you um propose some set of like code skills for it and then you'll try to use

[59:50.079] those skills to execute the task. You'll get an episode, you'll apply a reward model to it. Um, and if it succeeds, then you can put all those induced skills into your memory. But if not, then you could make some revisions to it. And there's a number of ways that skills might not succeed, right? So, um, one thing we could do is like apply a code llinter to an induced skill. So,

[01:00:15.520] here's a real example from the paper. There's this induced skill called identify pill. Um, you know, for like interacting with a drug website. And this uh function like takes a lot of arguments like you know the um the make of the pill the color but in the initial version of this skill that the agent wrote it actually didn't use all the parameters. So like it ignored this

[01:00:36.880] color parameter. So you could get feedback from a llinter on this skill and then sort of in the reflection type way um condition on that and then like you know uh create an updated version of the function and store that or like try executing that and store that. You could also use feedback from this reward model and condition on that when you're um

[01:01:00.400] making these revisions to the skill 2. So these are some nice benefits of code um that can be advantages even if you know the actual code function itself is a bit more rigid. Another nice benefit is that because these functions that are induced are now tool calls, it can really reduce the number of times that your agent needs to interact with the environment. So here's

[01:01:23.920] an example from um Zora's uh ASI paper. We have this uh task like uh updating a couple addresses on a page and for the base agent you have to you know like do all the very low-level actions of navigating through all these forms typing the particular um things from the address. But if we have this model that has induced these code skills, you can and this is a real example from uh from

[01:01:53.440] the work where we induce this navigate to address settings and update address details functions. We can actually solve this task in three steps where we um you know assuming that this is a good fit for the site. Um we can just call these two functions and um complete the task.

[01:02:12.319] Um, and the agent is actually much faster because it doesn't need to reobserve the website and then generate the tool call, then reobserve the new website, generate the new tool call. Um, as you'll probably see in the guey um, lecture that JY is giving, um, a really big bottleneck for these models is actually the number of times that they have to interact with the site because

[01:02:34.799] these images take up a lot of tokens and actually producing a chain of thought um, before each action takes up a lot of tokens too. All of those have to be generated. So efficiency is really important here. And um in this work we did find so we did a controlled comparison between using text skills and code skills. This was on a set of tasks which did have

[01:02:56.480] sort of more repeated structure. Um but we found that uh in comparison to no memory text skills um helped but code skills helped even more in terms of you know the accuracy of the system but also we got pretty big improvements in efficiency the number of times that the agent needed to interact with the page.

[01:03:18.960] Cool. So, as we've kind of talked about before, a big potential issue with skills is that they might not be general. And here's a failure case of this approach and actually a failure case of these code skills. So, we tried to see how well could skills generalize across websites. And we induced um these code skills on one site uh and then we tried to apply them on a real website uh

[01:03:43.920] like the Target shopping site. So this skill um that was induced on a different site worked on that site but like um uses assumes that this uh this um particular element that you're interacting with has a drop down like this. Whereas on the target site it's you know this set of radio buttons and so it it fails there. And um you have to have the model be able to like actually

[01:04:09.359] edit the skill based on um feedback from the environment as it's interacting with it. But code has a solution to this, right? Uh so we have um abstract classes and those can be instantiated in different ways. There's this uh paper called poly skill which does this. So um they're using code as the representation sort of building on this ASI work that we did.

[01:04:40.720] Um, but the first time that the model interacts with a new website, it writes an abstract class which doesn't have implementations for the methods, but could have stubs like searching for a product, adding to a cart, checking out. And um, then it'll also write a website specific implementation of it like this one for Amazon. Then when it's interacting with a different site, you

[01:05:02.480] could have some metadata or you could even just have the language model trigger that this particular concrete implementation no longer applies. and then you'll write a different instantiation of the abstract class. And they show that this helps too. Um, this is also nice because it gives you a way to have like a large number of specific skills, but only have a subset of them

[01:05:23.280] be active at a given time that are actually relevant. So, this kind of makes sense, right? It's, you know, just a software engineering best practice that's also applied to agents. Okay. Uh, yeah, we talked about all this already. um you guys had a good sense of the the pros and cons of each of these types of representation, but it's helpful to know that, you know, the

[01:05:45.760] skills standard allows you to combine both and um there's a lot of research to be done on the best way to combine these representations together. Um like uh said, okay, so we'll go quickly through a few papers um on different kind of like parts of this skill life cycle. This is a really open research topic of like what are the best ways to induce and

[01:06:08.240] manage these skills. Um you'll have the papers for for more details. Um but you can also explore this in your projects uh towards the end of the lecture or the end of the class if you're interested. Everything we've talked about so far has been learning from success, but it's also potentially pretty helpful to learn from failures. So say that the model

[01:06:31.599] like tries to carry out this task like um you know searching for Bluetooth headphones. Um but for this particular website they sort of have like their search terms are or rather than and so you get a list of everything that's Bluetooth or headphones or a Sony. This is a real example from this reasoning bench paper from Google. So you get like 5,000 results and the agent just breaks

[01:06:54.640] on this like it has to pagionate through all of these 5,000 results. it does, you know, it loses track of what the task is and it fails. But if we observe that um failed trajectory sort of in the reflection style way, we could uh produce some text that gives guidance on how to avoid it in the future. Like saying um we should give a more specific search term rather than this more

[01:07:18.880] general one and we should you know have like a larger number of items displayed so the model gets more in its context window at once. And this paper um generally uses the same framework as like uh agent workflow memory, agent skill induction, but instead of just having these kind of abstractions of the correct trajectories, it generates this text feedback um which um is applicable

[01:07:42.880] to failed trajectories too and is also you know the kind of thing that you would write in a skill yourself um if you were writing one and they find that this is pretty helpful. So these are different like types of memory. Um so synapse uses trajectories like full trajectories with all of the actions and observations all the tool calls and messages. Um this is agent

[01:08:06.640] workflow memory that uses these slightly abstracted parts of trajectories. And this is their approach that uses these text descriptions of strategies and um adding and negatives going you know adding and negative examples as inputs to the memory. um uh doesn't improve performance when you're using either trajectories or um workflows, but does improve substantially when you have sort of

[01:08:34.719] these text descriptions, which kind of makes sense given the example we saw before because you can describe in a general way how not to fail rather than remembering and conditioning on those failures. Another important thing to think about is we're deciding whether to store trajectories um you know store things in the memory or what type of strategies to

[01:09:02.000] infer from the examples based on whether we judged the example to be successful or not. That's in most of this work using a model as a judge that looks at the final state of the trajectory, looks at the task that you were trying to solve and predicts does it seem like I got it correct or not. So a really good question to ask here is what you know how much does the quality of that judge

[01:09:27.120] affect the performance of the algorithm because we know the judges aren't perfect. Um this paper reasoning bank controlled for this. So they um run their methods with a perfect judge. Um and they also like to so they use kind of the ground truth knowledge of whether it succeeded or not. Um but then they add some noise into that and so you're able to control um the accuracy the

[01:09:53.199] simulated accuracy of judging this trajectory and the performance does fall off but they find there's kind of a sweet spot where um you do get improvements from the memory um and uh there's sort of a widish range of accuracies where using the judge to induce the memory is helpful but there's definitely room to do future work here.

[01:10:19.600] Okay. And uh yeah, with the last few minutes, um I want to come back to we had a question before about does having more skills than are necessary um potentially hurt performance? And we also had a question about like um we're if we're retrieving skills from a set um does that retriever matter? Like does the quality of that retriever matter? So um there were some nice ablation

[01:10:46.960] experiments in this reasoning bank paper that uh control um how many experiences you are retrieving from the memory that you have and they show that performance does fall out fall off as you have more available. Um so this could be because of a couple different factors. So um you know maybe you just haven't run your agent on that many tasks and maybe

[01:11:14.960] there's nothing relevant in your memory. So putting more stuff in is just bound to be irrelevant. That would be sort of like just a fundamental limitation of this approach applied in that setting. Right? You can only learn if there's some similarities between the things you're learning from and the things you're applying to. But it could also be like a limitation of the model itself.

[01:11:37.840] Maybe the model gets thrown off by having more things available in the context window. That could potentially be fixed by training the model, right? To be better at not being distracted by irrelevant context, to be better at reasoning about what's actually relevant.

[01:11:56.080] And um yeah, it can also potentially be useful to uh explicitly reduce the size of your memory um so that there's less of a burden on the language model to select from the things that are in it. And um we did some work on this that sort of uses like a caching type approach um that you just look and see how often has a particular item in your memory been used in the past um and if

[01:12:22.719] it hasn't been used very frequently, you'll drop it. And this can you know improve this efficiency of the approaches quite a bit because you don't have to put as much in your context window but can also improve their success if the models are getting distracted by things that are irrelevant.

[01:12:41.520] Yeah. And the very last thing that we'll cover is so all of this was in some ways a little bit ad hoc, right? Like we were just having the language model look at these past experiences and then produce a skill which would be put in the memory and used in the future. But we're just like prompting the language model to predict things that seem like they might

[01:13:02.159] be useful in the future. And a really natural question is could you just train the language model to do that directly? Um you can. Um this is a direction that's starting to be explored just really recently. So these papers um are just appearing at you know just appeared at ACL um this year. But the basic idea here is that we're going to do reinforcement learning over multiple

[01:13:25.280] tasks seen in sequence. So this online learning setting that we've been covering for evaluation, we're also going to run training on it. We'll get multiple similar tasks in sequence and we'll be building up the memory. um in the same way that we've been doing before by inducing skills from the experience and using the memory on the future tasks. So this is a very complex,

[01:13:49.040] you know, process, right? Like we're using a couple different models here. Uh we're storing things in a memory. We're retrieving those. We're using them. But the good thing is reinforcement learning doesn't care. You can just apply reinforcement learning to complex non-ifferiable processes like this.

[01:14:04.960] We'll have a couple lectures that show you how. Um and you can get reward from uh did this second task succeed and did it use tasks that were induced in the past. So you can just do reinforcement learning on this reward being trained on um skill induction on sequences of similar tasks. And um there's a couple papers that have explored this. They both find that this is helpful. And uh

[01:14:35.280] one of them had this interesting result that um it helps to improve success if you also include this reward term that incentivizes reuse of the skills. So you could also imagine like introducing other sorts of reward terms that like minimize the size of the skill libraries that you've induced to try to you know kind of keep things regularized and not

[01:14:56.159] overfit too much. Um I think there's a lot of interesting like feature work that could be explored here. And um yeah that's uh that's all the time that we have. Uh but uh hopefully you got a sense for the way that skills are induced and also written. Um you'll apply those in your projects and you can explore them in the research projects too. I'll stick around for a few minutes

[01:15:19.040] if folks have any questions.
