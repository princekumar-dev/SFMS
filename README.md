# Student Feedback Management System

This project is a command-line Student Feedback Management System built with Python. It allows you to collect, analyze, and visualize student feedback for courses, including sentiment analysis and rating distribution charts.

## Features
- Add, delete, search, and display student feedback
- Sentiment analysis using TextBlob
- Emotion and key phrase extraction
- Rating distribution pie chart (matplotlib)
- Tabular display of feedback (tabulate)
- Data stored in a text file (`student_feedback.txt`)

## Requirements
- Python 3.8+
- pandas
- tabulate
- textblob
- matplotlib
- numpy
- python-dateutil
- pytz
- tzdata
- nltk
- click
- joblib
- regex
- tqdm
- colorama

## Setup
1. Create and activate a Python virtual environment:
   ```pwsh
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```pwsh
   pip install pandas tabulate textblob matplotlib numpy python-dateutil pytz tzdata nltk click joblib regex tqdm colorama
   python -m textblob.download_corpora
   ```

## Usage
Run the program:
```pwsh
C:/Users/princ/Downloads/projects/SFMS/.venv/Scripts/python.exe student_feedback_manager.py
```

Follow the menu prompts to add, delete, search, and analyze feedback.

## File Structure
- `student_feedback_manager.py`: Main program file
- `student_feedback.txt`: Data file (created automatically)

## Notes
- All feedback is stored in `student_feedback.txt` using pipe (`|`) as a separator.
- Sentiment and emotion analysis is performed automatically when feedback is added.
- Matplotlib is used for rating distribution visualization.

## License
MIT
