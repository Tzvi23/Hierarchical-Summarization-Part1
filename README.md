# Hierarchical-Summarization-Part1
The amount of written information that is around us at any moment is unimaginable. The written information can come in many different forms: news articles, study materials, articles, presentations, reports, etc. This information envelops us every moment on a variety of platforms such as computers, cell phones, tablets and more.

With the constantly growing amount of information, the need arises to automatically summarize this written information. One of the challenges in the summary is that it's difficult to generalize. For example, summarizing a news article is very different from summarizing a financial earnings report.

The goal of the project is to analyze a given financial text and create an hierarchical summarization structure. The final result of the process is a tree structure of the text with number of summaries with different topics.

The project is based on a data set of the Financial Narrative Summarization Workshop which includes 4000 non-structured annual reports of companies listed on the London Stock Exchange (LSE).

The project is based on two main methods: the topic modeling (TM) and discourse parsing.
The pipeline of the proposed methodology includes the following steps:
* Text pre-processing.
* Automated structure identification.
* Rhetorical Structure Theory (RST) tree construction, where sentences are splitted into two categories:
  * Nucleus - a nucleus representing the essence of that sentence.
  *  Satellite - the complementary part of the sentence.
  We extract only the Nucleuses for a summary, so that it contains only the main parts of the sentences.
* Topic Modeling – Build Latent Dirichlet Allocation (LDA) models based on the original data set.
* Sentence classification - Each sentence from the RST tree is classified into one of the topics obtained by TM. The classification uses the pre-trained topic models and gets the probabilities to belong to each of the topics, after which the number topic is set to be the max of the probabilities for the sentence.
* Hierarchical view of a document – A final document is built that includes all the processing steps and hierarchical tree view of the original text with the summaries.

The project evaluation is based on both extrinsic and intrinsic evaluation, using clustering and ROUGE metrics, respectively.

**Demo Video**
This project contains a functional GUI for the user to go throught the pipeline of creating a single hierarchical summary. <br>
GUI demo can be found in the following [Google-drive-link](https://drive.google.com/file/d/14qMRUhZIwaVoSltaLPSiH6NZx13M_9ue/view?usp=sharing) 

**Project Book** <br>
For extra information about the development of this project can be found at the [Project Book](https://drive.google.com/file/d/1PkugCj-p1JOip_eUMEjC5zfrXS267Gl-/view?usp=sharing)

**Important citations:** <br>
For the RST tree creation the project uses the CODRA project -
  Discourse Parser for English - [LINK](https://ntunlpsg.github.io/project/parser/parser/)

For the ROUGE evaluation the project uses the kavgan/ROUGE-2.0: <br>
Can be found at: https://github.com/kavgan/ROUGE-2.0
```
@article{ganesan2015rouge,
  title={ROUGE 2.0: Updated and Improved Measures for Evaluation of Summarization Tasks},
  author={Ganesan, Kavita},
  year={2015}
}
```
**Important Note:** <br>
Due to size limitations this code is partial and missing files that needed to run correctlly. <br>
[Part2](https://github.com/Tzvi23/Hierarchical-Summarization-Part2) of this project is the CODRA project with some small modification to work with the pipeline.
