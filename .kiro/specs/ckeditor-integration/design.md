# Design Document

## Introduction

This document provides the technical design for integrating CKEditor rich text editor into the Django admin panel for novel summary and chapter content fields. The design covers package installation, model field changes, configuration, data migration, and static file management.

## System Architecture

### Current Architecture
```
Plain Text Fields (Current):
NovelModel.summary → TextField
ChapterModel.content → TextField

Admin Interface:
Django Admin → Textarea widget → Plain text storage
```

### Target Architecture
```
Rich Text Fields (Target):
NovelModel.summary → RichTextField (CKEditor)
ChapterModel.content → RichTextField (CKEditor)

Admin Interface:
Django Admin → CKEditor widget → HTML storage
```

### Component Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django Admin  │    │   CKEditor      │    │   Database      │
│                 │    │   Widget        │    │                 │
│  - Novel Form   │───▶│  - Toolbar      │───▶│  - HTML Content │
│  - Chapter Form │    │  - HTML Editor  │    │  - Text Fields  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                         ┌───────────────┐
                         │ Static Files  │
                         │  - JS         │
                         │  - CSS        │
                         │  - Images     │
                         └───────────────┘
```

## Detailed Design

### 1. Package Installation and Configuration

#### 1.1 Package Installation
```bash
# Install django-ckeditor package
pip install django-ckeditor
```

#### 1.2 Django Settings Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ... existing apps ...
    'ckeditor',
    # ... other apps ...
]

# CKEditor configuration
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    },
}
```

### 2. Model Changes

#### 2.1 NovelModel Modification
```python
# Before (current)
from django.db import models

class NovelModel(models.Model):
    summary = models.TextField()
    # ... other fields ...

# After (target)
from django.db import models
from ckeditor.fields import RichTextField

class NovelModel(models.Model):
    summary = RichTextField(config_name='default')
    # ... other fields ...
```

#### 2.2 ChapterModel Modification
```python
# Before (current)
from django.db import models

class ChapterModel(models.Model):
    content = models.TextField()
    # ... other fields ...

# After (target)
from django.db import models
from ckeditor.fields import RichTextField

class ChapterModel(models.Model):
    content = RichTextField(config_name='default')
    # ... other fields ...
```

### 3. Data Migration Strategy

#### 3.1 Migration File Structure
```python
# migrations/0003_convert_to_richtext.py
from django.db import migrations
import html

def convert_text_to_html(apps, schema_editor):
    NovelModel = apps.get_model('core', 'NovelModel')
    ChapterModel = apps.get_model('core', 'ChapterModel')
    
    # Convert novel summaries
    for novel in NovelModel.objects.all():
        if novel.summary:
            # Convert plain text to HTML paragraphs
            html_content = '<p>' + html.escape(novel.summary).replace('\n', '</p><p>') + '</p>'
            novel.summary = html_content
            novel.save()
    
    # Convert chapter content
    for chapter in ChapterModel.objects.all():
        if chapter.content:
            # Convert plain text to HTML paragraphs
            html_content = '<p>' + html.escape(chapter.content).replace('\n', '</p><p>') + '</p>'
            chapter.content = html_content
            chapter.save()

def convert_html_to_text(apps, schema_editor):
    # Reverse migration - for rollback if needed
    from bs4 import BeautifulSoup
    
    NovelModel = apps.get_model('core', 'NovelModel')
    ChapterModel = apps.get_model('core', 'ChapterModel')
    
    # Convert novel summaries back to plain text
    for novel in NovelModel.objects.all():
        if novel.summary:
            soup = BeautifulSoup(novel.summary, 'html.parser')
            novel.summary = soup.get_text()
            novel.save()
    
    # Convert chapter content back to plain text
    for chapter in ChapterModel.objects.all():
        if chapter.content:
            soup = BeautifulSoup(chapter.content, 'html.parser')
            chapter.content = soup.get_text()
            chapter.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_genremodel_image'),
    ]
    
    operations = [
        migrations.AlterField(
            model_name='novelmodel',
            name='summary',
            field=RichTextField(config_name='default'),
        ),
        migrations.AlterField(
            model_name='chaptermodel',
            name='content',
            field=RichTextField(config_name='default'),
        ),
        migrations.RunPython(convert_text_to_html, convert_html_to_text),
    ]
```

### 4. Admin Interface Changes

#### 4.1 Admin Configuration
No changes needed to admin.py - CKEditor automatically replaces TextField widgets with RichTextField widgets in Django Admin.

### 5. Static Files Management

#### 5.1 Static File Configuration
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure CKEditor static files are included
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    # CKEditor static files are automatically discovered
]
```

#### 5.2 Collect Static Command
```bash
# Collect static files including CKEditor
python manage.py collectstatic --noinput
```

### 6. Fallback Mechanism

#### 6.1 Template Safe Display
```python
# In templates, use |safe filter to render HTML
{{ novel.summary|safe }}
{{ chapter.content|safe }}
```

#### 6.2 Fallback for Migration Issues
```python
def get_safe_content(content):
    """Safely get content with HTML fallback"""
    if not content:
        return ""
    
    # Check if content appears to be HTML
    if '<' in content and '>' in content:
        # Likely HTML, return as-is
        return content
    else:
        # Plain text, convert to HTML paragraphs
        return '<p>' + html.escape(content).replace('\n', '</p><p>') + '</p>'
```

## Technical Specifications

### 7.1 CKEditor Toolbar Configuration
```
Toolbar Items:
- Formatting: Bold, Italic, Underline, Strike
- Lists: NumberedList, BulletedList
- Links: Link, Unlink
- Alignment: JustifyLeft, JustifyCenter, JustifyRight, JustifyBlock
- Tools: RemoveFormat, Source (HTML view)
```

### 7.2 Field Specifications
```
NovelModel.summary:
- Type: RichTextField
- Config: 'default' CKEditor configuration
- Null: False (default)
- Blank: True (optional field)

ChapterModel.content:
- Type: RichTextField
- Config: 'default' CKEditor configuration
- Null: False (default)
- Blank: False (required field)
```

### 7.3 Database Schema Changes
```
Before Migration:
- novelmodel.summary: TEXT (plain text)
- chaptermodel.content: TEXT (plain text)

After Migration:
- novelmodel.summary: TEXT (HTML content)
- chaptermodel.content: TEXT (HTML content)
```

## Security Considerations

### 8.1 HTML Sanitization
- CKEditor provides basic HTML sanitization
- Django's |safe filter should only be used with trusted content
- Consider adding additional sanitization for user-generated content

### 8.2 Content Validation
```python
# Optional: Add custom validation for HTML content
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup

def validate_safe_html(value):
    """Validate that HTML doesn't contain unsafe tags"""
    soup = BeautifulSoup(value, 'html.parser')
    unsafe_tags = ['script', 'iframe', 'object', 'embed']
    
    for tag in unsafe_tags:
        if soup.find(tag):
            raise ValidationError(f'HTML contains unsafe tag: {tag}')
```

## Testing Strategy

### 9.1 Unit Tests
```python
# Test CKEditor field rendering
def test_novel_summary_richtext_field(self):
    novel = NovelModel.objects.create(
        title="Test Novel",
        summary="<p>Test <strong>bold</strong> content</p>"
    )
    self.assertIn('<strong>', novel.summary)

# Test data migration
def test_text_to_html_conversion(self):
    novel = NovelModel.objects.create(
        title="Test Novel",
        summary="Line 1\nLine 2\nLine 3"
    )
    # After migration should contain HTML
    self.assertIn('<p>', novel.summary)
```

### 9.2 Integration Tests
- Test CKEditor widget loads in Django Admin
- Test HTML content saves and retrieves correctly
- Test static files are properly served

### 9.3 Migration Tests
- Test forward migration converts text to HTML
- Test backward migration converts HTML to text
- Test data integrity after migration

## Deployment Checklist

### 10.1 Development Environment
- [ ] Install django-ckeditor package
- [ ] Add 'ckeditor' to INSTALLED_APPS
- [ ] Update model fields to RichTextField
- [ ] Create and apply migrations
- [ ] Test in local admin

### 10.2 Production Environment
- [ ] Install package on production server
- [ ] Run collectstatic to include CKEditor files
- [ ] Apply migrations during deployment
- [ ] Verify static files are served correctly
- [ ] Test admin functionality

## Dependencies

### 11.1 Python Packages
```
django-ckeditor==6.7.0
beautifulsoup4==4.12.0  # For migration rollback
```

### 11.2 Django Requirements
- Django >= 3.2
- Python >= 3.8
- Static files configured correctly

## Alternatives Considered

### 12.1 Alternative Rich Text Editors
- **Django Summernote**: Lighter but less feature-rich
- **TinyMCE**: More features but larger bundle size
- **Quill.js**: Modern but requires more integration work

### 12.2 Chosen Solution Rationale
- CKEditor has excellent Django integration
- Mature and stable with good documentation
- Appropriate feature set for novel content
- Automatic widget replacement in Django Admin

## Limitations and Future Considerations

### 13.1 Current Limitations
- No image upload support (intentional - not needed for novel text)
- Limited to basic formatting tools
- HTML storage increases database size slightly

### 13.2 Future Enhancements
- Custom CKEditor configurations per field type
- Image upload support if needed later
- Content versioning for chapter edits
- Preview functionality in admin

## Glossary

- **RichTextField**: Django field that stores HTML content and provides CKEditor widget
- **CKEditor Config**: Configuration dictionary defining toolbar items and editor settings
- **Migration**: Django database schema change with data transformation
- **Static Files**: JavaScript, CSS, and images required by CKEditor
- **HTML Sanitization**: Process of removing unsafe HTML tags from content