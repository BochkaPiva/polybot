poliom_bot/
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker compose configuration
├── Dockerfile                # Docker configuration
├── main.py                   # Entry point for the bot
├── config.py                 # Configuration settings
├── bot/
│   ├── __init__.py
│   ├── handlers/             # Message and callback handlers
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication handlers
│   │   ├── menu.py           # Menu navigation handlers
│   │   ├── search.py         # Knowledge base search handlers
│   │   └── common.py         # Common handlers (start, help, etc.)
│   ├── keyboards/            # Keyboard builders
│   │   ├── __init__.py
│   │   ├── menu.py           # Menu keyboards
│   │   └── common.py         # Common keyboards
│   ├── middlewares/          # Middlewares
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication middleware
│   │   └── throttling.py     # Rate limiting middleware
│   ├── filters/              # Custom filters
│   │   ├── __init__.py
│   │   └── auth.py           # Authentication filters
│   └── utils/                # Utility functions
│       ├── __init__.py
│       └── db.py             # Database utility functions
├── db/
│   ├── __init__.py
│   ├── base.py               # Base database setup
│   ├── models.py             # SQLAlchemy models
│   └── repositories/         # Database repositories
│       ├── __init__.py
│       ├── users.py          # User repository
│       └── menu.py           # Menu repository
├── search/
│   ├── __init__.py
│   ├── client.py             # OpenSearch client
│   ├── indexer.py            # Document indexing
│   └── searcher.py           # Search functionality
└── admin/                    # Admin panel (will be developed later)
    └── __init__.py
\`\`\`

Now, let's create the basic files needed to get started:
