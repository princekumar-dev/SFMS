import pandas as pd
from tabulate import tabulate
import os
from datetime import datetime
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt

class StudentFeedbackManager:
    def __init__(self, file_path='student_feedback.txt'):
        self.file_path = file_path
        self.columns = [
            'Registration_No', 'Student_Name', 'Course', 'Feedback',
            'Sentiment', 'Sentiment_Score', 'Subjectivity', 'Emotions',
            'Key_Phrases', 'Rating', 'Date'
        ]
        self.emotion_keywords = {
            'positive': ['excellent', 'great', 'good', 'amazing', 'wonderful', 'helpful', 'love', 'enjoy', 'best'],
            'negative': ['bad', 'terrible', 'poor', 'worst', 'difficult', 'hard', 'confusing', 'boring', 'waste'],
            'neutral': ['okay', 'fine', 'average', 'normal', 'regular', 'usual', 'standard']
        }
        self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                self.df = pd.read_csv(self.file_path, sep='|')
                for col in self.columns:
                    if col not in self.df.columns:
                        self.df[col] = ''
                self.df['Registration_No'] = self.df['Registration_No'].astype(str)
            except pd.errors.EmptyDataError:
                self.df = pd.DataFrame(columns=self.columns)
        else:
            self.df = pd.DataFrame(columns=self.columns)
        self.df = self.df.sort_values('Registration_No')

    def save_data(self):
        self.df.to_csv(self.file_path, sep='|', index=False)

    def extract_emotions(self, text):
        text = text.lower()
        emotions = []
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotions.append(emotion)
        return list(set(emotions))

    def extract_key_phrases(self, text):
        sentences = text.split('.')
        key_phrases = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 3:
                key_phrases.append(sentence)
        return key_phrases[:3]

    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        score = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        if score > 0.1:
            sentiment = "Positive"
        elif score < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        emotions = self.extract_emotions(text)
        key_phrases = self.extract_key_phrases(text)
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'subjectivity': round(subjectivity, 2),
            'emotions': emotions,
            'key_phrases': key_phrases
        }

    def format_table(self, df):
        display_df = df.copy()
        display_df.columns = [
            'Registration No', 'Student Name', 'Course', 'Feedback',
            'Sentiment', 'Score', 'Subjectivity', 'Emotions',
            'Key Phrases', 'Rating', 'Date'
        ]
        def format_score(x):
            try:
                if pd.isnull(x) or x == '' or str(x).strip() == '':
                    return "N/A"
                return f"{float(x):.2f}"
            except Exception:
                return "N/A"
        display_df['Score'] = display_df['Score'].apply(format_score)
        display_df['Subjectivity'] = display_df['Subjectivity'].apply(format_score)
        return display_df

    def add_feedback(self, reg_no, name, course, feedback, rating):
        reg_no = str(reg_no)
        if not self.df.empty and reg_no in self.df['Registration_No'].values:
            print(f"Error: Registration number {reg_no} already exists!")
            return False
        try:
            rating = int(rating)
            if rating < 1 or rating > 10:
                print("Error: Rating must be between 1 and 10!")
                return False
        except ValueError:
            print("Error: Rating must be a number between 1 and 10!")
            return False
        analysis = self.analyze_sentiment(feedback)
        new_entry = {
            'Registration_No': reg_no,
            'Student_Name': str(name),
            'Course': str(course),
            'Feedback': str(feedback),
            'Sentiment': analysis['sentiment'],
            'Sentiment_Score': analysis['score'],
            'Subjectivity': analysis['subjectivity'],
            'Emotions': ', '.join(analysis['emotions']) if analysis['emotions'] else 'None',
            'Key_Phrases': ' | '.join(analysis['key_phrases']) if analysis['key_phrases'] else 'None',
            'Rating': rating,
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)
        self.df = self.df.sort_values('Registration_No')
        self.save_data()
        print("\nNew Feedback Entry Added:")
        print("=" * 100)
        display_df = self.format_table(pd.DataFrame([new_entry]))
        print(tabulate(display_df, headers='keys', tablefmt="grid", showindex=False))
        print("=" * 100)
        return True

    def delete_feedback(self, reg_no=None, name=None):
        if self.df.empty:
            print("No feedback entries found!")
            return False
        if reg_no:
            reg_no = str(reg_no)
            initial_len = len(self.df)
            self.df = self.df[self.df['Registration_No'] != reg_no]
            if len(self.df) < initial_len:
                self.save_data()
                print(f"Feedback for Registration Number {reg_no} deleted.")
                return True
            else:
                print(f"No entry found for Registration Number {reg_no}.")
                return False
        elif name:
            initial_len = len(self.df)
            self.df = self.df[self.df['Student_Name'].str.lower() != str(name).lower()]
            if len(self.df) < initial_len:
                self.save_data()
                print(f"Feedback for Student Name '{name}' deleted.")
                return True
            else:
                print(f"No entry found for Student Name '{name}'.")
                return False
        else:
            print("Please provide either Registration Number or Student Name.")
            return False

    def search_feedback(self, reg_no=None, name=None):
        if self.df.empty:
            print("No feedback entries found!")
            return
        if reg_no:
            reg_no = str(reg_no)
            result = self.df[self.df['Registration_No'] == reg_no]
        elif name:
            result = self.df[self.df['Student_Name'].str.lower() == str(name).lower()]
        else:
            print("Please provide either Registration Number or Student Name.")
            return
        if result.empty:
            print("No matching feedback found.")
        else:
            print("\nSearch Results:")
            print("=" * 100)
            display_df = self.format_table(result)
            print(tabulate(display_df, headers='keys', tablefmt="grid", showindex=False))
            print("=" * 100)

    def display_all(self):
        if self.df.empty:
            print("No feedback entries found!")
            return
        print("\nAll Feedback Entries:")
        print("=" * 100)
        display_df = self.format_table(self.df)
        print(tabulate(display_df, headers='keys', tablefmt="grid", showindex=False))
        print("=" * 100)

    def display_rating_chart(self):
        if self.df.empty:
            print("No feedback entries found!")
            return
        try:
            self.df['Rating'] = pd.to_numeric(self.df['Rating'], errors='coerce')
            valid_ratings = self.df.dropna(subset=['Rating'])
            if valid_ratings.empty:
                print("No valid ratings found!")
                return
            rating_categories = {
                'Excellent (9-10)': (9, 10),
                'Very Good (7-8)': (7, 8),
                'Good (5-6)': (5, 6),
                'Fair (3-4)': (3, 4),
                'Poor (1-2)': (1, 2)
            }
            category_counts = {}
            for category, (min_rating, max_rating) in rating_categories.items():
                count = len(valid_ratings[(valid_ratings['Rating'] >= min_rating) & (valid_ratings['Rating'] <= max_rating)])
                if count > 0:
                    category_counts[category] = count
            if not category_counts:
                print("No ratings found in any category!")
                return
            plt.figure(figsize=(12, 8))
            colors = ['#2ecc71', '#3498db', '#f1c40f', '#e67e22', '#e74c3c']
            wedges, texts, autotexts = plt.pie(category_counts.values(),
                                               labels=category_counts.keys(),
                                               autopct='%1.1f%%',
                                               startangle=90,
                                               colors=colors[:len(category_counts)],
                                               textprops={'fontsize': 12})
            for autotext in autotexts:
                autotext.set_fontweight('bold')
            plt.title('Distribution of Ratings', pad=20, fontsize=16, fontweight='bold')
            plt.legend(wedges, category_counts.keys(),
                       title="Rating Categories",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
            plt.tight_layout()
            plt.show()
            print("\nRating Statistics:")
            print("=" * 100)
            print(f"Average Rating: {valid_ratings['Rating'].mean():.2f}")
            print(f"Highest Rating: {valid_ratings['Rating'].max()}")
            print(f"Lowest Rating: {valid_ratings['Rating'].min()}")
            print(f"Total Ratings: {len(valid_ratings)}")
            print("=" * 100)
        except Exception as e:
            print(f"Error creating rating chart: {str(e)}")
            return

    def get_sentiment_summary(self):
        if self.df.empty:
            print("No feedback entries found!")
            return
        self.df['Sentiment_Score'] = pd.to_numeric(self.df['Sentiment_Score'], errors='coerce')
        self.df['Subjectivity'] = pd.to_numeric(self.df['Subjectivity'], errors='coerce')
        sentiment_counts = self.df['Sentiment'].value_counts()
        avg_scores = self.df.groupby('Sentiment')['Sentiment_Score'].mean().round(2)
        avg_subjectivity = self.df.groupby('Sentiment')['Subjectivity'].mean().round(2)
        summary_data = []
        for sentiment in ['Positive', 'Neutral', 'Negative']:
            count = sentiment_counts.get(sentiment, 0)
            avg_score = avg_scores.get(sentiment, 0)
            avg_subj = avg_subjectivity.get(sentiment, 0)
            summary_data.append([
                sentiment,
                count,
                f"{avg_score:.2f}",
                f"{avg_subj:.2f}"
            ])
        print("\nDetailed Sentiment Analysis Summary:")
        print("=" * 100)
        print(tabulate(summary_data,
                      headers=['Sentiment', 'Count', 'Avg Score', 'Avg Subjectivity'],
                      tablefmt="grid"))
        all_emotions = []
        for emotions in self.df['Emotions'].dropna():
            all_emotions.extend(emotions.split(', '))
        emotion_counts = Counter(all_emotions)
        print("\nEmotion Distribution:")
        print("=" * 100)
        emotion_data = [[emotion, count] for emotion, count in emotion_counts.items()]
        print(tabulate(emotion_data, headers=['Emotion', 'Count'], tablefmt="grid"))
        total_entries = len(self.df)
        overall_avg = self.df['Sentiment_Score'].mean()
        overall_subj = self.df['Subjectivity'].mean()
        print("\nOverall Statistics:")
        print(f"Total Entries: {total_entries}")
        print(f"Overall Average Sentiment Score: {overall_avg:.2f}")
        print(f"Overall Average Subjectivity: {overall_subj:.2f}")
        print("=" * 100)
        self.display_rating_chart()

def main():
    manager = StudentFeedbackManager()
    while True:
        print("\n=== Student Feedback Management System ===")
        print("1. Add Feedback")
        print("2. Delete Feedback")
        print("3. Search Feedback")
        print("4. Display All Feedback")
        print("5. Show Advanced Sentiment Analysis")
        print("6. Show Rating Distribution")
        print("7. Exit")
        choice = input("\nEnter your choice (1-7): ")
        if choice == '1':
            reg_no = input("Enter Registration Number: ")
            name = input("Enter Student Name: ")
            course = input("Enter Course: ")
            feedback = input("Enter Feedback: ")
            rating = input("Enter Rating (1-10): ")
            manager.add_feedback(reg_no, name, course, feedback, rating)
        elif choice == '2':
            print("\nDelete by:")
            print("1. Registration Number")
            print("2. Student Name")
            delete_choice = input("Enter your choice (1-2): ")
            if delete_choice == '1':
                reg_no = input("Enter Registration Number: ")
                manager.delete_feedback(reg_no=reg_no)
            elif delete_choice == '2':
                name = input("Enter Student Name: ")
                manager.delete_feedback(name=name)
            else:
                print("Invalid choice!")
        elif choice == '3':
            print("\nSearch by:")
            print("1. Registration Number")
            print("2. Student Name")
            search_choice = input("Enter your choice (1-2): ")
            if search_choice == '1':
                reg_no = input("Enter Registration Number: ")
                manager.search_feedback(reg_no=reg_no)
            elif search_choice == '2':
                name = input("Enter Student Name: ")
                manager.search_feedback(name=name)
            else:
                print("Invalid choice!")
        elif choice == '4':
            manager.display_all()
        elif choice == '5':
            manager.get_sentiment_summary()
        elif choice == '6':
            manager.display_rating_chart()
        elif choice == '7':
            print("Thank you for using the Student Feedback Management System!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
