#include <wx/wx.h>
#include <wx/textctrl.h>
#include <curl/curl.h>
#include <fstream>
#include <thread>

size_t write_data(void* ptr, size_t size, size_t nmemb, FILE* stream) {
	size_t written = fwrite(ptr, size, nmemb, stream);
	return written;
}

void descargar_video(const std::string& url) {
	CURL* curl;
	FILE* fp;
	CURLcode res;
	std::string outfilename = "descargado.mp4";
	curl = curl_easy_init();
	if (curl) {
		fp = fopen(outfilename.c_str(),"wb");
		curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
		res = curl_easy_perform(curl);
		curl_easy_cleanup(curl);
		fclose(fp);
	}
}

class MyApp : public wxApp {
public:
	virtual bool OnInit();
};

class MyFrame : public wxFrame {
public:
	MyFrame(const wxString& title);

	void OnButtonClicked(wxCommandEvent& event);

	wxTextCtrl* textCtrl;
};

IMPLEMENT_APP(MyApp)

bool MyApp::OnInit() {
	MyFrame* frame = new MyFrame("Descargar video");
	frame->Show(true);
	return true;
}

MyFrame::MyFrame(const wxString& title)
	: wxFrame(NULL, wxID_ANY, title) {
	this->SetSize(800, 600);

	wxPanel* panel = new wxPanel(this, wxID_ANY);

	wxBoxSizer* vbox = new wxBoxSizer(wxVERTICAL);

	textCtrl = new wxTextCtrl(panel, wxID_ANY, wxEmptyString, wxDefaultPosition, wxSize(300, 30));
	vbox->Add(textCtrl, 0, wxALL, 10);

	wxButton* button = new wxButton(panel, wxID_ANY, "Descargar video", wxDefaultPosition, wxSize(150, 50));
	button->Bind(wxEVT_BUTTON, &MyFrame::OnButtonClicked, this);
	vbox->Add(button, 0, wxALL, 10);

	panel->SetSizer(vbox);
}

void MyFrame::OnButtonClicked(wxCommandEvent& event) {
	std::string url = textCtrl->GetValue().ToStdString();
	std::thread t(descargar_video, url);
	t.detach();
	wxMessageBox("La descarga del video ha comenzado.", "Descarga", wxOK | wxICON_INFORMATION);
}