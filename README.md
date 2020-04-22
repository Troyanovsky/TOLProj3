# Overview
This repo is created for Tools for Online Learning Project 3 at Carnegie Mellon University. The goal of the project is to utilize learnersoucring for creating a set of quiz questions based on students' responses.

The project team members are: Guodong Zhao, Junhui Yao, and Shujing Lin. Guodong was responsible for creating the problem generation code; Junhui was responsible for providing learning theory support and writeup; Shujing was responsible for creating the prototype website based on the generated quiz problem sets.

The tolProj3.py python code is used for generating the questions for the new quiz.
The code essentially does the following:
1. Clean up the questions data and answers data (e.g. trim unnecessary texts for question types, pick relevant data tags etc.) and store them in dictionaries for later use.
2. Identify correct and incorrect student responses (Details to follow in the next section).
3. Generate new questions based on the student responses in Step 2, along with the corresponding feedback.
4. Store the generate problem set in to a .txt file.

# GitHub Repo and Prototype Website:
GitHub Repo: https://github.com/Troyanovsky/TOLProj3

Prototype Website: https://troyanovsky.github.io/TOLProj3/

Google Colab Notebook for Generating Questions: https://colab.research.google.com/drive/1iP7fF8tfMaIy-FEb2C_Ey4EakGh_Oufc

Google Colab Notebook for Validation: https://colab.research.google.com/drive/1Jbv2exs_w2xFJtJRaG6E0yj-wo6rwzun

# How are correct answers selected?
The criteria for selecting correct answers are as below:
1. **Correction of the multiple-choice or select-all-that-apply questions.** We first picked out the student responses with a full-mark on the corresponding multiple-choice or select-all-that-apply questions because there is a strong correlation between the correction of the choices and of the free responses.
2. **Similarity between free responses and the correct answers text.** Within the responses from Step 1, we further filtered out the students responses that are not very similar to the correct answer text. To calculate this similarity, both the student's free response and the correct answer text were tokenized and cleaned (e.g. removed stop words) using the nltk (natural language toolkit) python library and converted into vectors to calculate the cosine similarity using the following formula:
![alt text](https://sites.temple.edu/tudsc/files/2017/03/cosine-equation.png)

We filtered out the student responses that have a similarity outside of one standard deviation of the average similarities of the correct student response pool.
3. **Length of the student response.** From the selected student response pool in Step2, we further filtered out the student responses with lenghts outside of one standard deviation of the correct student response pool.

The reason for this mechanism would be that communication of one similar idea requires analogical word length and choices. Plus, objective assessment could be a good indicator of
performance assessment. 

# How are the incorrect answers selected?
**The incorrect answers were selected by taking the student responses that got a score of 0 for the multiple-choice or select-all-that-apply questions.** If there are not enough student responses with a score of 0, the requirement is relaxed to responses with a score of 0.5.

Initially, I wanted to also filter out the responses that are too similar to the correct answer text. However, by texting the code on the dataset, I have identified that some questions (especially Question 3 in the original dataset) do not have enough incorrect student responses to choose from. Therefore, I have to remove this requirement of similarity. The score requirement was also initially strict that only responses with a score of 0 would be chose, but the same thing happened that not enough incorrect responses are generated. Therefore, the requirement is relaxed to 0.5 in the case that there are not enough responese.

# How are the new questions generated?
From the previous two sections, we would have two pools of answers: one for correct answers and one for incorrect answers. 

Since the number of incorrect answers is small, the generator function will first try to see if there are more than 3 incorrect answers. If there is, the genreator function will randomly pick 3 incorrect answers and 1 correct answer and mark this question as a multiple choice question. If there is not enough incorrect answers, the generator function will randomly pick 3 correct answers and 1 incorrect answer and mark this question as a select-all-that-apply question.

# Pick options for retry
Students can easily retry the questions or the entire problem set they got wrong if they want to. As I have described in the previous section, **the options of the problem are picked randomly from a pool of correct and incorrect answers**. Therefore, everytime the code is run, a completely new problem set will be generated. Students can retry the entire problem set just by running the code again to generate a set of questions with random new options and problem types.

Students would have the opportunity of **reassessing the mastery if they fail at the first attempt**. We design it as a whole retake instead of targeting the particular question. Understandably, retaking the failed ones will help students learn. Nevertheless, we are worried that the limited number of questions may not fully demonstrate students’ understanding of the knowledge embedded in the questions. **Through taking the second quiz, we hope to double-check their understanding.**


# Feedback after student answers a question
For each question, the texts for the original correct answers were noted and will be included in the generated new question. Students will get their correction feedback from whether they answered right or wrong and **will get a sample correct answer from the original correct answer texts**.

The feedback also belongs to goal-oriented feedback in a broader sense. Goal feedback is  “the goal statement was based on the conclusion of the next inference on the optimal proof path and stated the current correct subgoal”  (McKendre, 1990, p. 391). We choose not to provide constraint-based feedback since it might confuse students especially when the difference is subtle. 

# Testing code on validation set
The code was run on the validation set, the generated questions with answer choices, feedback, and question type are **printed at the bottom of the page** and also in the problemSet.txt file.

**The code worked pretty well for the validation set**, even though the validation set has some different formatting than the development set. What is surprising is that **there are also no issues of not enough of incorrect answer choices** (this was a problem for the development set) and both questions generated are multiple-choice questions.

# Reflection and Future Improvement
A comment based on the development and validation is that **it will be easier to filter out confusing choices if the dataset is bigger** and the learner sourcing result will be more usable.

Since the dataset was small for the development set, I had to make compromises while selecting incorrect answer choices - I cannot trim out more questions other than choosing the student responses with lower scores because there are not enough incorrect student responses. If the dataset were bigger, **I would add in the selection criteria of similarity** by filtering out the answer choices that are too similar to the correct answer choice.

With these future improvements, the robustness and reliability of the generated problem sets will be improved.

# Reference
McKendree, J. (1990). Effective feedback content for tutoring complex skills.Human-Computer Interaction, 5(4), 381-413. doi:10.1207/s15327051hci0504_2