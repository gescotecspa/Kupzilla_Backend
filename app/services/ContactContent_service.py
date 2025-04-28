from app.models.contact_content import ContactContent
from app import db

class ContactContentService:
    @staticmethod
    def get_content_by_id(content_id):
        return ContactContent.query.get(content_id)

    @staticmethod
    def get_all_contents():
        return ContactContent.query.all()

    @staticmethod
    def create_content(language, html_content):
        new_content = ContactContent(language=language, html_content=html_content)
        db.session.add(new_content)
        db.session.commit()
        return new_content

    @staticmethod
    def update_content(content_id, language, html_content):
        content = ContactContentService.get_content_by_id(content_id)
        if content:
            content.language = language
            content.html_content = html_content
            db.session.commit()
            return content
        else:
            return None

    @staticmethod
    def delete_content(content_id):
        content = ContactContentService.get_content_by_id(content_id)
        if content:
            db.session.delete(content)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_content_by_language(language):
        return (ContactContent.query
                .filter_by(language=language)
                .order_by(ContactContent.created_at.desc())
                .first())