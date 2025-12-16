# Case 02: Mixin class method name error
# Difficulty: Hard
# Method comes from a Mixin class, harder to trace

from models.article import Article

def main():
    article = Article("Python Tips", "Learn Python...", "tech")
    # Error: 'to_jason' should be 'to_json' - method from SerializableMixin
    data = article.to_jason()
    print(data)

if __name__ == "__main__":
    main()
