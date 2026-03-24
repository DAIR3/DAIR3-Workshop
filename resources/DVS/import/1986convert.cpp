//1986convert.cpp by: Derek Onken
//

#include <fstream>
#include <string>
#include <iostream>
#include <ctime>

using namespace std;
static int error1 =0;
static int error2 =0;
static int error3 =0;
static int error4 =0;

static int fulls[16] = {/*7,*/36,66,95,124/*t*/,154,183,212,242,272,301/*t*/,331,361,391,420,450,479/*t*/};//jan 1, 1985 = 1, these are the dates of full moons
//Jan 7, feb 5, mar 7, apr 5,may 4,jun 3, jul 2, jul 31, aug 30, sep 29, oct 28,nov 27,dec 27,jan26,feb 24,mar 26, apr 24
static int loc=15;

int deltaMoon1986 (int conDate){
	if(conDate < 37){
		error1++;
		if (conDate<0){
			error3++;
		}
		return -98;
	}
	if (loc < 0){
		error2++;
		return -99;
	}
	int deltaMoon = fulls[loc] - conDate;
			if (deltaMoon > 0){
				loc--;
				deltaMoon = deltaMoon1986(conDate);
			}
			loc=15;
	return deltaMoon;

}


int main(){

	int i;
	clock_t start = clock();


ifstream file;
ofstream csv;
ofstream gest;
ofstream term;

file.open("NATL1986.txt");
//file.open("TestTxt.txt");
csv.open("TestResults1986.csv",ios::app);
term.open("termPreg1986.csv",ios::app);
gest.open("oldTerm1986.csv",ios::app);



string raw;

csv << "Year of birth,residence state,reporting area,blank(certificate #),resident(1=yes 2=no),resident status,place of residence," <<
		"place of occurence,sex,attendant at birth,father race, mother race,child race,child race recode,mother age," <<
		"mother age recode36,mother age recode15,mother age recode12,mother age recode8,mother age recode7,mother age recode6," <<
		"#children born alive(still living),#children born alive(now dead),#children born dead,total birth order," <<
		"total birth order recode9,live birth order,lbirth order recode9,birth order recode8,birth order recode7," <<
		"birth order recode6,birth order recode3,reserved position,father age,father age recode 11,birthweight(grams)," <<
		"birthweight recode12,birthweight recode3,place of delivery,plurality,plurality recode3,plurality recode2,birth MMDD,date of last menstration," <<
		"gestation(weeks),gestation recode10,gestation recode3,mother education,mother edu recode14,mother edu recode6,father education," <<
		"father edu recode14,marital status,marital status recode2,month in pregnancy when prenatal care began,month prenatal began recode10," <<
		"month prenatal began recode6,date of last live birth(MM19YY)(7777=none),interval(months)since last live birth, interval recode17," <<
		"interval recode10,interval recode8,date of last termination(MM19YY)(7777=none),last termination flag,interval(months) since last termination," <<
		"interval(months) since termination of last pregnancy,interval since termination of last preg recode9,outcome of last pregnancy," <<
		"mother's birthplace,total number of prenatal visits,congenital malformation,reserved(3spots),flags regarding place of residence," <<
		"flags for place of occurence,reserved(3),attendant @ birth,number of other terminations before 20 weeks,number of other terminations 20weeks &after," <<
		"one minute apgar,one min. apgar recode5,five minute apgar, five min. apgar recode5,origin descent mother, origin descent father, gestation imputation flag," <<
		"region of residence,region of occurence,occurence using Fed Info Processing Standards Geo Codes,record weight,number prenatal vists recode28," <<
		"number prenatal visits recode12, reserved, expanded state of occurence,number of days that conception date occurs after most recent full moon,\n";

term << "Year of birth,residence state,reporting area,blank(certificate #),resident(1=yes 2=no),resident status,place of residence," <<
		"place of occurence,sex,attendant at birth,father race, mother race,child race,child race recode,mother age," <<
		"mother age recode36,mother age recode15,mother age recode12,mother age recode8,mother age recode7,mother age recode6," <<
		"#children born alive(still living),#children born alive(now dead),#children born dead,total birth order," <<
		"total birth order recode9,live birth order,lbirth order recode9,birth order recode8,birth order recode7," <<
		"birth order recode6,birth order recode3,reserved position,father age,father age recode 11,birthweight(grams)," <<
		"birthweight recode12,birthweight recode3,place of delivery,plurality,plurality recode3,plurality recode2,birth MMDD,date of last menstration," <<
		"gestation(weeks),gestation recode10,gestation recode3,mother education,mother edu recode14,mother edu recode6,father education," <<
		"father edu recode14,marital status,marital status recode2,month in pregnancy when prenatal care began,month prenatal began recode10," <<
		"month prenatal began recode6,date of last live birth(MM19YY)(7777=none),interval(months)since last live birth, interval recode17," <<
		"interval recode10,interval recode8,date of last termination(MM19YY)(7777=none),last termination flag,interval(months) since last termination," <<
		"interval(months) since termination of last pregnancy,interval since termination of last preg recode9,outcome of last pregnancy," <<
		"mother's birthplace,total number of prenatal visits,congenital malformation,reserved(3spots),flags regarding place of residence," <<
		"flags for place of occurence,reserved(3),attendant @ birth,number of other terminations before 20 weeks,number of other terminations 20weeks &after," <<
		"one minute apgar,one min. apgar recode5,five minute apgar, five min. apgar recode5,origin descent mother, origin descent father, gestation imputation flag," <<
		"region of residence,region of occurence,occurence using Fed Info Processing Standards Geo Codes,record weight,number prenatal vists recode28," <<
		"number prenatal visits recode12, reserved, expanded state of occurence,number of days that conception date occurs after most recent full moon,\n";


//int x=0;
while(file.good()  ){
//	x++;

	getline(file, raw);


	
	/*
	SUPER UBER MASSIVELY IMPORTANT: our array index starts at 0 and the raw data manual index starts at 1
	*/
	csv <<  "198" <<  raw[0] << ","//year of birth
		<< raw[1] << raw[2] << ","	//expanded state of residence 
		<< raw[3] << ","	//reporting area
		<< raw[4] << raw[5] << raw[6] << raw[7] << raw[8] << raw[9] << "," //blank, for certificate number
		<< raw[10] << "," // resident (1) or nonresident(2)
		<< raw[11] << "," ;//resident status
		for(i=12;i<27;i++){
			csv << raw[i];	//place of residence
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
		<< raw[39] << "," //child race recode 3
		<< raw[40] << raw[41] << "," //mother age
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
		<< raw[212] << "," //reserved
		<< raw[213] << raw[214] << ","; //expanded state of occurence




	//find full term preganancies aka "term" aka 37-41 weeks of gestation
	int gestWeek = raw[92]-'0';//char to int
	gestWeek = gestWeek*10 +(raw[93]-'0');

	if (gestWeek >=37 && gestWeek<=41){

		gest << raw[83] << raw[84] << raw[85] << raw[86] << "198" << raw[0] << "," //date of birth
			 <<	raw[34] << "," //sex
			 << raw[87] <<raw[88] <<raw[89] << raw[90] << "198" << raw[91] << "," //date of last menstrual cycle
			 << raw[92] << raw[93] << "," //gestation in weeks
			 << raw[190] << "," //gestation imputation flag
			 << raw[59] << ","; //birth order recode 9

		//1988 is a leap year
		int birthMonth = (raw[83] -'0')*10 + (raw[84]-'0');
		int birthDate = (raw[85] -'0')*10 + (raw[86]-'0');
		if (birthDate == 99){
			birthMonth = -1;
		}
		//int intDate
		switch (birthMonth){
			case 1: 
			break;
			case 2:
				birthDate += 31;
				break;
			case 3:
				birthDate += 59;//february has 28 days
				break;
			case 4:
				birthDate += 90;
				break;
			case 5:
				birthDate += 120;
				break;
			case 6:
				birthDate += 151;
				break;
			case 7:
				birthDate += 181;
				break;
			case 8:
				birthDate += 212;
				break;
			case 9:
				birthDate += 243;
				break;
			case 10:
				birthDate += 273;
				break;
			case 11:
				birthDate += 304;
				break;
			case 12:
				birthDate += 334;
				break;
			default:
				birthDate = -366;//birthMonth is 99
				break;
		}
		//cout << birthDate << endl;
		birthDate += 365;//we shift the dates on the dates of birth so that 1= Jan 1, 1985
		int conDate;
		gest << birthDate << ",";
		
		
		int birthOrder = raw[59]-'0';//char to int
		
		if (birthOrder == 1){
				conDate = birthDate - 270;
		}
		else if (birthOrder == 2){
				conDate = birthDate - 269;
		}
		else if (birthOrder > 2){
				conDate = birthDate - 268;
		}
		if (birthOrder == 9){
			conDate = -2;
		}

		gest << conDate << "," ;//conception date

		int deltaMoon = deltaMoon1986(conDate);
		gest << deltaMoon*(-1) << "," << "\n";//number of days that conception date is after the most recent full moon
		csv << deltaMoon*(-1) << "," << "\n";
		


		term <<  "198" <<  raw[0] << ","//year of birth
		<< raw[1] << raw[2] << ","	//expanded state of residence 
		<< raw[3] << ","	//reporting area
		<< raw[4] << raw[5] << raw[6] << raw[7] << raw[8] << raw[9] << "," //blank, for certificate number
		<< raw[10] << "," // resident (1) or nonresident(2)
		<< raw[11] << "," ;//resident status
		for(i=12;i<27;i++){
			term << raw[i];	//place of residence
		}
		term << "," ;
		for(i=27;i<34;i++){
			term << raw[i];	//place of occurence
		}
		term << ",";
		term << raw[34] << "," //sex
		<< raw[35] << "," //attendant at birth
		<< raw[36] << "," //father race
		<< raw[37] << "," //mother race
		<< raw[38] << "," //child race
		<< raw[39] << "," //child race recode 3
		<< raw[40] << raw[41] << "," //mother age
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
			term << raw[i];	//flags for place of residence
		}
		term << ",";
		for(i=160;i<172;i++){
			term << raw[i];	//flags for place of occurence
		}
		term << ",";
		term << raw[172] << raw[173] << raw[174] << "," //reserved
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
			term << raw[i];	//occurence: Federal Information Processing Standards Geographic Codes
		}
		term << ",";
		term << raw[207] << "," //record weight....should be 1 for all values after 1985
		<< raw[208] << raw[209] << "," //number of prenatal visits recode 28
		<< raw[210] << raw[211] << "," // number of prenatal visits recode 12
		<< raw[212] << "," //reserved
		<< raw[213] << raw[214] << "," //expanded state of occurence
		<< deltaMoon*(-1) << "," << "\n";
		if (deltaMoon*(-1)<0 || deltaMoon*(-1) >30){
			error4++;
		}

//		int sex = (raw[34]-'0');
//		if (sex == 1){
//			male << deltaMoon*(-1) << ",";
//		}
//		else if (sex == 2){
//			female << deltaMoon*(-1) << ",";
//		}
		//else{
			//i dont know yet
	//	}
	}
	else{
		csv << "-100,\n";//not term
	}
}

file.close();
csv.close();
gest.close();
term.close();

double duration = (clock()-start)/(double) CLOCKS_PER_SEC;
	cout << "time takes " << duration << " seconds" << endl;
	cout << "error1 = " << error1 << endl;
	cout << "error2 = " << error2 << endl;
	cout << "error3 = " << error3 << endl;
	cout << "error4 = " << error4 << endl;

	return 0;
}

