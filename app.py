from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_admin import Admin
from datetime import datetime

# ... other imports ...

app = Flask(__name__)
admin = Admin(app)

# Add the admin routes
@app.route('/admin')
@app.route('/admin/')
def admin_dashboard():
    return render_template('admin/dashboard.html')




@app.route('/admin/pages')
def admin_pages():
    return render_template('admin/pages.html')

@app.route('/admin/pages/create', methods=['GET'])
def create_page_form():
    return render_template('admin/create_page.html')

@app.route('/api/v1/admin/pages', methods=['POST'])
def create_page():
    try:
        data = request.get_json()
        # Process your data here
        # Save to database
        return jsonify({'message': 'Page created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/about-islam/edit/<int:id>', methods=['GET', 'POST'])
def admin_about_islam_edit(id):
    # Get the page
    page = AboutIslamPage.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update page
            page.title = request.form.get('title')
            page.slug = request.form.get('slug')
            page.content = request.form.get('content')
            page.updated_at = datetime.utcnow()
            
            # Debug print
            print("Content being saved:", page.content)
            
            db.session.commit()
            flash('Page updated successfully!', 'success')
            return redirect(url_for('admin_about_islam'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating page: {str(e)}', 'error')
            return render_template('admin/about_islam/edit.html', page=page)
    
    # Debug print
    print("Content being loaded:", page.content)
    
    return render_template('admin/about_islam/edit.html', page=page)







# Make sure this is at the end of your file
if __name__ == '__main__':
    app.run(debug=True) 