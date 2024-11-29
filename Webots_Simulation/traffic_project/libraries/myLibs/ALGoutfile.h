#pragma once

#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include<string.h>
#include<iostream>
#include <iomanip>
#include <string>
#include <fstream>

using namespace std;

// void Exel_Output(string name, std::ios_base::openmode my_mode, float a[], int j, string discription); 
// void file_create(string name, std::ios_base::openmode my_mode);


void Exel_Output(string name,std::ios_base::openmode my_mode,float a[],int j,string discription)
{
	ofstream outfile(name, my_mode);
	if(!outfile)
	{
		cerr<<"open error!"<<endl;
		exit(1);
	}
	// cout << name << " ok" << endl;
    outfile << discription << "\t"; 	
    for (int i = 0; i < j;i++)
	{
		outfile<< a[i] <<"\t";			
	}
    outfile << "\n";					
    outfile.close();
}

void Txt_Output(string name,std::ios_base::openmode my_mode,double a[],int j){
    ofstream outfile(name, my_mode);
	if(!outfile)
	{
		std::cerr << "Unable to open file " + name << std::endl;
		exit(1);
	}
	// cout << name << " ok" << endl;
    for (int i = 0; i < j;i++)
	{
        if(i==j-1){
            outfile<< a[i];
        }
        else{
            outfile<< a[i] <<",";			
        }
	}
    outfile << "\n";					
    outfile.close();
}

void Txt_Output(string name,std::ios_base::openmode my_mode,double a[], int j,string extraString){
    ofstream outfile(name, my_mode);
	if(!outfile)
	{
		std::cerr << "Unable to open file " + name << std::endl;
		exit(1);
	}
	// cout << name << " ok" << endl;
    for (int i = 0; i < j;i++)
	{
		outfile << a[i] <<",";
	}
	outfile << extraString;
    outfile << "\n";					
    outfile.close();
}

void Txt_Output(string name,std::ios_base::openmode my_mode,float *a,int j){
    ofstream outfile(name, my_mode);
	if(!outfile)
	{
		std::cerr << "Unable to open file " + name << std::endl;
		exit(1);
	}
	// cout << name << " ok" << endl;
    for (int i = 0; i < j;i++)
	{
        if(i==j-1){
            outfile<< a[i];
        }
        else{
            outfile<< a[i] <<",";			
        }
	}
    outfile << "\n";					
    outfile.close();
}

string Txt_Input(string name){
	ifstream inputFile(name);
    
    if (!inputFile) {
        std::cerr << "Unable to open file " + name << std::endl;
        return string("error");
    }
    string line;
	string out;
    
    while (getline(inputFile, line)) {
		out += line;
    }
    
    inputFile.close();
	
	return out;
}

void Txt_Input(string name, string *buffer, int size){
	ifstream inputFile(name);
    
    if (!inputFile) {
        std::cerr << "Unable to open file " + name << std::endl;
    }
    string line;
	int count = 0;
    
    while (getline(inputFile, line)) {
		
		if (!line.empty() && line[line.length() - 1] == '\n') {
			line.erase(line.length() - 1);
		}
		buffer[count] = line;
		if((++count)>=size){
			break;
		}
    }
    
    inputFile.close();
}

void Txt_Input(string name, double *buffer, int size){
	ifstream inputFile(name);
    
    if (!inputFile) {
        std::cerr << "Unable to open file " + name << std::endl;
    }
    string line;
	int count = 0;
    
    while (getline(inputFile, line)) {
		
		if (!line.empty() && line[line.length() - 1] == '\n') {
			line.erase(line.length() - 1);
		}
		buffer[count] = stod(line);
		if((++count)>=size){
			break;
		}
    }
    
    inputFile.close();
}

std::streampos get_file_size(std::string file_path) {
    std::ifstream file(file_path, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        return -1;
    }
    
    std::streampos file_size = file.tellg(); 
    file.close();
    return file_size;
}

bool file_exists(std::string file_path) {
    std::ifstream file(file_path);
    return file.is_open();
}

bool delete_file(const std::string file_path) {
    if (std::remove(file_path.c_str()) != 0) {
        std::cerr << "Error deleting file: " << file_path << std::endl;
        return false;
    } else {
        std::cout << "File successfully deleted: " << file_path << std::endl;
        return true;
    }
}


void file_create(string name, std::ios_base::openmode my_mode)
{
	ofstream outfile(name, my_mode);
	if (!outfile)
	{
		cerr << "open error!" << endl;
		exit(1);
	}
	// cout << name << " ok" << endl;
	outfile.close();
}
////////////////////////////////////////////////////////////////////////////////