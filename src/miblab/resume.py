import os
import csv
import subprocess
import pylatex as pl
from pylatex.utils import NoEscape, bold

class Resume(pl.Document):
    """
    Generate professional PDFs optimized for resumes using a PyLaTeX framework.
    
    Parameters
    ----------
    folder : str
        Path to the folder where the resume should be saved.
    filename : str
        Name of the file (without the .pdf extension).
    name : str
        The applicant's full name.
    title : str  
        Professional headline or job title (e.g., 'Senior Research Scientist').
    email : str
        Professional contact email.
    phone : str
        Contact phone number.
    location : str
        City, Country or State.
    linkedin : str
        LinkedIn profile or portfolio URL.
    profile_pic : str, optional
        Path to a headshot image file.
    """

    def __init__(
            self,
            folder,
            filename='my_resume',
            name='John Doe', 
            title='Professional Title', 
            email='johndoe@email.com',
            phone='+1 234 567 890',
            location='London, UK',
            linkedin='linkedin.com/in/johndoe',
            profile_pic=None      
        ):

        # Configure standard article class for tight, clean layout matching resume conventions
        super().__init__(documentclass='article', document_options=['10pt', 'a4paper'])
        
        self.folder = folder
        self.filename = filename
        
        setup_resume(
            self, name, title, email, phone, location, linkedin, profile_pic
        )

    def add_section(self, title):
        """Add a clean, accented resume section divider."""
        self.append(NoEscape(r'\vspace{0.3cm}'))
        # Using a custom tcolorbox banner for resume section styling
        self.append(NoEscape(
            r'\begin{tcolorbox}[colback=gray!15,colframe=gray!60,arc=2mm,boxrule=0.5pt,left=2mm,right=2mm,top=1mm,bottom=1mm]'
            r'{\large\bfseries\sffamily ' + title + r'}'
            r'\end{tcolorbox}'
        ))
        self.append(NoEscape(r'\vspace{-0.1cm}'))

    def add_experience(self, role, company, dates, description_items):
        """Add a structured work or project experience block with bullet points."""
        self.append(NoEscape(r'\noindent'))
        self.append(bold(role) if hasattr(self, 'append') else role)
        self.append(NoEscape(f' | {company} \\hfill {dates}\\\\'))
        
        # Inject bullet points using enumitem with tight spacing
        self.append(NoEscape(r'\begin{itemize}[noitemsep,topsep=2pt,leftmargin=0.5cm]'))
        for item in description_items:
            # Simple fallback for character cleaning inside list strings
            for char in ['_', '#', '$', '%', '&']:
                item = item.replace(char, '\\' + char)
            self.append(NoEscape(f'\\item {item}'))
        self.append(NoEscape(r'\end{itemize}'))
        self.append(NoEscape(r'\vspace{0.2cm}'))

    def build(self):
        """Compile the resume PDF using our clean exception handler."""
        build_resume_pdf(self, self.folder, self.filename)


def setup_resume(doc: pl.Document, name, title, email, phone, location, linkedin, profile_pic):
    # Core aesthetic layout packages
    doc.packages.append(pl.Package('geometry', options=['margin=0.60in']))
    doc.packages.append(pl.Package('hyperref', options=['hidelinks']))
    doc.packages.append(pl.Package('tcolorbox'))
    doc.packages.append(pl.Package('enumitem'))
    doc.packages.append(pl.Package('graphicx'))
    doc.packages.append(pl.Package('array'))
    
    # Remove standard paragraph indentations
    doc.append(NoEscape(r'\setlength{\parindent}{0pt}'))
    
    # Constructing a 2-column header grid using tabular
    # Column 1: Left-aligned contact credentials. Column 2: Profile Picture frame.
    if profile_pic and os.path.exists(profile_pic):
        clean_pic_path = os.path.abspath(profile_pic).replace('\\', '/')
        
        doc.append(NoEscape(r'\begin{tabular}{m{12.5cm} r}'))
        # Information side
        info_block = (
            r'{\Huge\bfseries\sffamily ' + name + r'}\\[0.15cm]'
            r'{\large\color{gray}\bfseries\sffamily ' + title + r'}\\[0.3cm]'
            r'\textbf{Email:} ' + email + r' \ | \ \textbf{Phone:} ' + phone + r'\\'
            r'\textbf{Location:} ' + location + r' \ | \ \textbf{LinkedIn:} \url{' + linkedin + r'}'
        )
        doc.append(NoEscape(info_block))
        doc.append(NoEscape('&'))
        # Portrait side
        doc.append(NoEscape(r'\includegraphics[width=2.8cm,height=2.8cm,keepaspectratio]{' + clean_pic_path + r'}'))
        doc.append(NoEscape(r'\end{tabular}'))
    else:
        # Graceful no-picture fallback that standardizes formatting dynamically
        doc.append(NoEscape(r'{\Huge\bfseries\sffamily ' + name + r'}\\[0.15cm]'))
        doc.append(NoEscape(r'{\large\color{gray}\bfseries\sffamily ' + title + r'}\\[0.3cm]'))
        doc.append(NoEscape(f'\\textbf{{Email:}} {email} \\ | \\ \\textbf{{Phone:}} {phone} \\ | \\ \\textbf{{Location:}} {location}\\\\'))
        doc.append(NoEscape(r'\textbf{LinkedIn:} \url{' + linkedin + r'}'))
        
    doc.append(NoEscape(r'\\[0.2cm]'))


def build_resume_pdf(doc: pl.Document, folder, filename):
    outputpath = os.path.join(folder, filename + '_source')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
        
    try:
        doc.generate_pdf(
            filename, 
            clean=True, 
            clean_tex=False, 
            compiler='pdfLaTeX', 
            compiler_args=['-output-directory', outputpath],
        )
        
        # Cleanly transfer the generated PDF file up to your parent execution directory
        src_pdf = os.path.join(outputpath, filename + '.pdf')
        dst_pdf = os.path.join(folder, filename + '.pdf')
        if os.path.exists(src_pdf):
            if os.path.exists(dst_pdf):
                os.remove(dst_pdf)
            os.rename(src_pdf, dst_pdf)
            
    except subprocess.CalledProcessError as e:
        latex_logs = e.output.decode('utf-8', errors='replace') if e.output else "No log output found."
        error_lines = [line for line in latex_logs.splitlines() if line.startswith('!') or 'Error' in line]
        summary = "\n".join(error_lines) if error_lines else "Review log directly."
        raise RuntimeError(f"Resume compilation failed:\n{summary}")