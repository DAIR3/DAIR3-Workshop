//convertAll.cpp by: Derek Onken 10/4/14
//

#include <fstream>
#include <string>
#include <iostream>
#include <ctime>
#include <sstream>


using namespace std;

int dayToInt(string MMDDYYYY);

//most likely portion for error; every entry should be of the form MMDD of full moon
//manually entered from NASA website
//null strings are fillers so that every row has the same length
static string fullsStr[21][13]={{"0115","0214","0314","0413","0512","0610","0710","0808","0906","1006","1105","1204",""},//1968
							{"0103","0202","0304","0402","0502","0531","0629","0729","0827","0925","1025","1123","1223"},//1969	
							{"0122","0221","0323","0421","0521","0619","0718","0817","0915","1014","1113","1212",""},//1970
							{"0111","0210","0312","0410","0510","0609","0708","0806","0905","1004","1102","1202","1231"},//1971
							{"0130","0229","0329","0428","0528","0626","0726","0824","0923","1022","1120","1220",""},//1972
							{"0118","0217","0318","0417","0517","0615","0715","0814","0912","1012","1110","1210",""},//1973
							{"0108","0206","0308","0406","0506","0604","0704","0803","0901","1001","1031","1129","1229"},//1974
							{"0127","0226","0327","0425","0525","0623","0723","0821","0920","1020","1118","1218",""},//1975
							{"0117","0215","0316","0414","0513","0612","0711","0809","0908","1008","1106","1206",""},//1976
							{"0105","0204","0305","0404","0503","0601","0701","0730","0828","0927","1026","1125","1225"},//1977
							{"0124","0223","0324","0423","0522","0620","0720","0818","0916","1016","1114","1214",""},//1978
							{"0113","0212","0313","0412","0512","0610","0709","0808","0906","1005","1104","1203",""},//1979
							{"0102","0201","0301","0331","0430","0529","0628","0727","0826","0924","1023","1122","1221"},//1980
							{"0120","0218","0320","0419","0519","0617","0717","0815","0914","1013","1111","1211",""},//1981
							{"0109","0208","0309","0408","0508","0606","0706","0804","0903","1003","1101","1201","1230"},//1982
							{"0128","0227","0328","0427","0526","0625","0724","0823","0922","1021","1120","1220",""},//1983
							{"0118","0217","0317","0415","0515","0613","0713","0811","0910","1009","1108","1208",""},//1984
							{"0107","0205","0307","0405","0504","0603","0702","0731","0830","0929","1028","1127","1227"},//1985
							{"0126","0224","0326","0424","0523","0622","0721","0819","0918","1017","1116","1216",""},//1986
							{"0115","0213","0315","0414","0513","0611","0711","0809","0907","1007","1105","1205",""},//1987
							{"0104","0202","0303","0402","0501","0531","0629","0729","0827","0925","1025","1123","1223"}};//1988
int fulls[260]={0};


void generateFullArray(){
	int fullsSize=0;
	int i,j;

	for(i=0;i<21;i++){
		for(j=0;j<13;j++){
			if (fullsStr[i][j] != ""){
				fullsSize++;
			}
		}
	}
	/*	fullsSize = sizeof(fulls1969)/sizeof(fulls1969[0]) + sizeof(fulls1968)/sizeof(fulls1968[0])
				+ sizeof(fulls1970)/sizeof(fulls1970[0]) + sizeof(fulls1971)/sizeof(fulls1971[0]) + sizeof(fulls1972)/sizeof(fulls1972[0])
				+ sizeof(fulls1973)/sizeof(fulls1973[0]) + sizeof(fulls1974)/sizeof(fulls1974[0]) + sizeof(fulls1975)/sizeof(fulls1975[0])
				+ sizeof(fulls1976)/sizeof(fulls1976[0]) + sizeof(fulls1977)/sizeof(fulls1977[0]) + sizeof(fulls1978)/sizeof(fulls1978[0])
				+ sizeof(fulls1979)/sizeof(fulls1979[0]) + sizeof(fulls1980)/sizeof(fulls1980[0]) + sizeof(fulls1981)/sizeof(fulls1981[0])
				+ sizeof(fulls1982)/sizeof(fulls1982[0]) + sizeof(fulls1983)/sizeof(fulls1983[0]) + sizeof(fulls1984)/sizeof(fulls1984[0])
				+ sizeof(fulls1985)/sizeof(fulls1985[0]) + sizeof(fulls1986)/sizeof(fulls1986[0]) + sizeof(fulls1987)/sizeof(fulls1987[0])
				+ sizeof(fulls1988)/sizeof(fulls1988[0]);//should be 19*12 + 7 = 235
	*/
	if (fullsSize != 260){//should be 21*12 + 8 = 260
		std::cout << "incorrect fulls length" << endl;
	}

	
	
	//int moons[235];

	int k=0;
	string year="";

	for(i=0;i<21;i++){
		//year = to_string(1970+i);//only good in c++ post c++11

		stringstream ss;
		ss << (1968+i);
		string year = ss.str();
		
		
		for(j=0;j<13;j++){
			if (fullsStr[i][j] != "" && k < 260){
				fulls[k] = dayToInt(fullsStr[i][j] + year);
				k++;
			}
			else if( k>259){
				std::cout << "moons array out of bounds" << endl;
			}
		}
	}
	
	for(k=0; k<259;k++){
		if (fulls[k+1]-fulls[k] > 30 || fulls[k+1]-fulls[k] < 29){
			std::cout << "entry error on entry: " << k << endl;//one error first time checked
		}
		if (fulls[k] >= fulls[k+1]){
			std::cout << "moons not sorted" << endl;	
		}
		
	}
	//std::cout << fullsSize <<endl;


	return;
}


void printFulls(){
	for (int k=0; k<260 ; k++){
		std::cout << fulls[k] << ", " ;
	}
	std::cout <<endl;
	return;
}

int calcPostFull(int conception){//calculate the number of days after the most recent full moon
	if(conception < 0 ){
		return -90;
	}
	
	int startIndex = conception/30 + 5;//gives a start index relatively close to the correct value to keep while iterations small
										// the 30 comes from the approximate number days between full moons
										//also, (1988-1968 + 1)*365.25 / 30 ~ 256  which is < 260
										//that is (highest value for a full moon)/30 <= 256
	int i = startIndex;
	//int postFull;
	while ((conception - fulls[i]) < 0){
		
		//cout << (conception - fulls[i]) << endl;
		i--;
	}
	
	return conception - fulls[i];
}

int dayToInt(string MMDDYYYY){//MMDDYYYY because I'm American
	int date=0;
	string monthStr = MMDDYYYY.substr(0,2);
	string dayStr = MMDDYYYY.substr(2,2);
	string yearStr = MMDDYYYY.substr(4,4);

	//cout << monthStr << "/" << dayStr << "/" << yearStr << endl;

	int month = atoi(monthStr.c_str());//equivalent to c++11 stoi(monthStr)
	if (month>12){
		return -80;
	}
	int day = atoi(dayStr.c_str());
	if (day>31){
		return -80;
	}
	int year = atoi(yearStr.c_str());

	//std::cout << month << "," << day << "," << year << endl;

	date = (year-1968) * 365;
	if (year>1968){
		if (year > 1972){
			date++;
			if(year >1976){
				date++;
				if(year>1980){
					date++;
					if(year>1984){//data only goes up to 1988
							date++;
					}
				}
			}
		}
	}
	if (month > 1){
		date+=31;
		if(year%4 == 0 && month > 2){//leap year
			date+=29;
		}
		else if (year%4 !=0 && month>2){
			date+=28;
		}
		if (month>3){
			date+=31;
			if (month>4){
				date+=30;
				if (month>5){
					date+=31;
					if(month>6){
						date+=30;
						if(month>7){
							date+=31;
							if(month>8){
								date+=31;
								if(month>9){
									date+=30;
									if (month>10){
										date+=31;
										if (month>11){
											date+=30;
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}//closes if (month>1)

	date+=day;


	return date;
}


void parseFile(string year, string csvName){

	cout << "year " << year << " beginning parsing" <<endl;

	int error4=0;

if (year.length()!=4){
	std::cout << "invalid string entry on year: " << year << endl;
	return;

}
string yearPrefix = year.substr(0,3);

ifstream file;
ofstream csv;


string inputFile = "NATL" + year + ".txt";
//string inputFile = "TestTxt" + year + ".txt";
file.open(inputFile.c_str());
csv.open(csvName.c_str(),ios::app);

	string raw;




try{



double x=0;

//while(file.good()){// && x < 3913788){
//	x++;
getline(file,raw);

while(!file.eof()){
	int i;

//	getline(file, raw);
	
	
	

	/*
	SUPER UBER MASSIVELY IMPORTANT: our array index starts at 0 and the raw data manual index starts at 1
	*/
	

csv <<  yearPrefix <<  raw[0] << "," ;//year of birth
		if (atoi(year.c_str()) > 1981){
			csv << raw[1] << raw[2] << ","	;//expanded state of residence.......//shipment number pre1982		 
		}
		else {
			csv << "  ," ;//changed to shipment number which we remove
		}
		csv << raw[3] << ","	//reporting area
		<< raw[4] << raw[5] << raw[6] << raw[7] << raw[8] << raw[9] << "," //blank, for certificate number
		<< raw[10] << "," // resident (1) or nonresident(2)
		<< raw[11] << "," ;//resident status
		for(i=12;i<27;i++){
			csv << raw[i];	//place of residence.........21-23 switch SMSA codes from 1979 to 1980
		}
		csv << "," ;
		for(i=27;i<34;i++){
			csv << raw[i];	//place of occurence
		}
		csv << ",";
		csv << raw[34] << "," //sex
		<< raw[35] << "," //attendant at birth
		<< raw[36] << "," //father race
		<< raw[37] << "," //mother race
		<< raw[38] << "," //child race
		<< raw[39] << "," ;//child race recode 3

		//cout << "checkpoint " << x << endl;
	csv	<< raw[40] << raw[41] << "," //mother age
		<< raw[42] << raw[43] << "," //mother age recode 36
		<< raw[44] << raw[45] << "," //mother age recode 15
		<< raw[46] << raw[47] << "," //mother age recode 12
		<< raw[48] << "," //mother age recode 8
		<< raw[49] << "," //mother age recode 7
		<< raw[50] << "," //mother age recode 6
		<< raw[51] << raw[52] << "," //number of children born alive, still living //see 1984 note
		<< raw[53] << raw[54] << "," //number children born alive, now dead        //see 1984 note
		<< raw[55] << raw[56] << "," //number children born dead
		<< raw[57] << raw[58] << "," //detail total bith order
		<< raw[59] << "," //total birth order recode 9
		<< raw[60] << raw[61] << "," //detail live birth order
		<< raw[62] << "," //live birth order recode 9
		<< raw[63] << "," //live birth order recode 8
		<< raw[64] << "," //live birth order recode 7
		<< raw[65] << "," //live birth order recode 6
		<< raw[66] << "," //live birth order recode 3
		<< raw[67] << ","//reserved position
		<< raw[68] << raw[69] << "," //father age
		<< raw[70] << raw[71] << "," //father age recode 11
		<< raw[72] << raw[73] << raw[74] << raw[75] << "," //birthweight in grams
		<< raw[76] << raw[77] << "," //birthweight recode 12
		<< raw[78] << "," //birthweight recode 3
		<< raw[79] << "," //place of delivery
		<< raw[80] << "," //plurality
		<< raw[81] << "," //plurality recode 3
		<< raw[82] << "," //plurality recode 2
		<< raw[83] << raw[84] << raw[85] << raw[86] << "," // month and day of birth
		<< raw[87] << raw[88] << raw[89] << raw[90]  << "198"  << raw[91] << "," //date of last menstrual period MMDDYYYY
		<< raw[92] << raw[93] << "," //gestation in weeks
		<< raw[94] << raw[95] << "," //gestation recode 10
		<< raw[96] << ","//gestation recode 3
		<< raw[97] << raw[98] << ","//mother education
		<< raw[99] << raw[100] << ","//mother education recode 14
		<< raw[101] << ","			//mother education recode 6
		<< raw[102] << raw[103] << ","//father education
		<< raw[104] << raw[105] << ","//father education recode 14
		<< raw[106] << "," //marital status
		<< raw[107] << "," //marital status recode 2
		<< raw[108] << "," //month of pregnancy when prenatal care began
		<< raw[109] << raw[110] << "," // month prenatal care began recode 10
		<< raw[111] << "," //month prenatal care began recode 6
		<< raw[112] << raw[113] << raw[114] << raw[115] << "," //date of last live birth MM19YY; 7777 = none
		<< raw[116] << raw[117] << raw[118] << "," //interval (months) since last live birth
		<< raw[119] << raw[120] << "," // interval (months) since last live birth recode 17
		<< raw[121] << raw[122] << "," //interval (months) since last live birth recode 10
		<< raw[123] << "," //interval (months) since last live birth recode 8
		<< raw[124] << raw[125] << raw[126] << raw[127] << "," //date of last termination MM19YY; 7777 = none
		<< raw[128] << "," //last termination flag
		<< raw[129] << raw[130] << raw[131] << "," //interval(months) since last termination
		<< raw[132] << raw[133] << raw[134] << "," //interval(months) since termination of last pregnancy
		<< raw[135] << "," //interval since termination of last pregnancy recode 9
		<< raw[136] << "," //outcome of last pregnancy
		<< raw[137] << raw[138] << "," //mother's place of birth
		<< raw[139] << raw[140] << "," //total number of prenatal visits
		<< raw[141] << "," //congenital malformation
		<< raw[142] << raw[143] << raw[144] << "," ;//reserved
		for(i=145;i<160;i++){
			csv << raw[i];	//flags for place of residence
		}
		csv << ",";
		for(i=160;i<172;i++){
			csv << raw[i];	//flags for place of occurence
		}
		csv << ",";
		csv << raw[172] << raw[173] << raw[174] << "," //reserved
		<< raw[175] << "," //attendant at birth
		<< raw[176] << raw[177] << "," //number of other terminations before 20 weeks
		<< raw[178] << raw[179] << "," //number of other terminations 20 weeks and after
		<< raw[180] << raw[181] << "," //one minute apgar score
		<< raw[182] << ","	 //one minute apgar recode 5
		<< raw[183] << raw[184] << "," // five minute apgar score
		<< raw[185] << "," //five minute apgar recode 5
		<< raw[186] << raw[187] << ","  //origin of descent of mother
		<< raw[188] << raw[189] << ","  //origin of descent of father
		<< raw[190] << "," //gestation imputation flag
		<< raw[191] << "," //region of residence
		<< raw[192] << ","; //region of occurence
		for(i=193;i<207;i++){
			csv << raw[i];	//occurence: Federal Information Processing Standards Geographic Codes
		}
		csv << ",";
		csv << raw[207] << "," //record weight....should be 1 for all values after 1985
		<< raw[208] << raw[209] << "," //number of prenatal visits recode 28
		<< raw[210] << raw[211] << "," // number of prenatal visits recode 12
		<< raw[212] << "," ;//reserved
		if (atoi(year.c_str()) > 1981){
			csv << raw[213] << raw[214] << ","; //expanded state of occurence	 
		}
		else {
			csv << "  ," ;//changed to reserved
		}




	//find full term preganancies aka "term" aka 37-41 weeks of gestation
	string gest = raw.substr(92,2);
	
	int gestWeek = atoi(gest.c_str());

	if (gestWeek >=37 && gestWeek<=41){

		string DOB = raw.substr(83,4) + yearPrefix + raw.substr(0,1);
		//std::cout << DOB << endl;
		
		//string DOB2 = raw[83] + raw[84] + raw[85] + raw[86] + yearPrefix + raw[0];
		//std::cout << DOB2 << endl;

		
		int dobInt = dayToInt(DOB);
		
		int conDate;
		
		int birthOrder = atoi((raw.substr(59,1)).c_str());//simplify
		
		if (birthOrder == 1){
				conDate = dobInt - 270;
		}
		else if (birthOrder == 2){
				conDate = dobInt - 269;
		}
		else if (birthOrder > 2){
				conDate = dobInt - 268;
		}
		if (birthOrder == 9){
			conDate = -2;
		}

		

		int deltaMoon = calcPostFull(conDate);
		
		csv << deltaMoon << "," << "\n";//number of days that conception date is after the most recent full moon
			
		if (deltaMoon<0 || deltaMoon >30){
			error4++;
		}

	}
	else{
		csv << "-100,\n";//not term
	}



getline(file,raw);

}//close while

}//close try
catch (exception e){
	cout << e.what() << endl;
	

}
//csv << "\n" ;

file.close();
csv.close();


//double duration = (clock()-start)/(double) CLOCKS_PER_SEC;
	//std::cout << "time takes " << duration << " seconds" << endl;
	//std::cout << "error1 = " << error1 << endl;
	//std::cout << "error2 = " << error2 << endl;
	//std::cout << "error3 = " << error3 << endl;
	std::cout << "error4 = " << error4 << endl;

	return;
}









int main(){

	clock_t start = clock();

	int i;
	
	generateFullArray();
	printFulls();
	
	ofstream csv;
	string totalFile = "natalityCalc.csv";
	csv.open(totalFile.c_str(),ios::app);

	csv << "DT_YEAR,ID_STATE,ID_AREA,ID_CERT,IN_RESIDENT,ID_RES_STATUS,ID_RESIDENCE,ID_OCCURENCE,ID_SEX,ID_ATTENDANT,"<<
		"ID_F_RACE,ID_M_RACE,ID_C_RACE,ID_C_RACE3,AM_M_AGE,AM_M_AGE36,AM_M_AGE15,AM_M_AGE12,AM_M_AGE8,AM_M_AGE7,AM_M_AGE6,"<<
		"AM_CHILDREN _BASL,AM_CHILDREN_BAND,AM_CHILDREN_BD,AM_TOT_B_ORDER,AM_TOT_B_ORDER9,AM_LIVE_B_ORDER,AM_LIVE_B_ORDER9,"<<
		"AM_LIVE_B_ORDER8,AM_LIVE_B_ORDER7,AM_LIVE_B_ORDER6,AM_LIVE_B_ORDER3,RESERVED,AM_F_AGE,AM_F_AGE11,AM_BIRTHWEIGHT,"<<
		"AM_BRITHWEIGHT12,AM_BIRTHWEIGHT3,ID_DELIVERY_LOC,AM_PLURALITY,AM_PLURALITY3,AM_PLURALITY2,DT_BIRTH_MMDD,DT_LAST_MENSES,"<<
		"AM_GESTATION,AM_GESTATION10,AM_GESTATION3,ID_M_EDU,ID_M_EDU14,ID_M_EDU6,ID_F_EDU,ID_F_EDU14,IN_MARRIED,IN_MARRIED2,"<<
		"AM_PRENATAL,AM_PRENATAL10,AM_PRENATAL6,DT_LAST_LB_MM19YY,AM_POST_LAST_LB,AM_POST_LAST_LB17,AM_POST_LAST_LB10,AM_POST_LAST_LB8,"<<
		"DT_LAST_TERMIN,IN_LAST_TERMIN,AM_POST_LT,AM_POST_TLP,AM_POST_TLP9,ID_LAST_PREG,ID_M_BIRTHPLACE,AM_TOT_PRENATAL,IN_MALFORMATION,"<<
		"RESERVED2,IN_REPORT_FLAGS,IN_OCCUR_FLAGS,RESERVED3,ID_ATTENDANT_NCHS,AM_TERMINATION<20,AM_TERMINATION>20,AM_1MIN_APGAR,"<<
		"AM_1MIN_APGAR5,AM_5MIN_APGAR,AM_5MIN_APGAR5,ID_M_DESCENT,ID_F_DESCENT,IN_GEST_FLAG,ID_RES_REGION,ID_OCC_REGION,ID_FIPS_OCC,"<<
		"ID_WEIGHT_REC,AM_PRENATAL28,AM_PRENATAL12,RESERVED4,ID_STATE_OCC,AM_POST_FULL,\n";//also stored in titles2.csv
	csv.close();

	for (i = 1988; i>1968 ; i--){
		stringstream ss;
		ss << (i);
		string year = ss.str();
		parseFile(year, "natalityCalc.csv");

		cout << "year " << i<< " parsed" <<endl;

	}

	double duration = (clock()-start)/(double) CLOCKS_PER_SEC;
	std::cout << "time takes " << duration << " seconds" << endl;

return 0;

}
