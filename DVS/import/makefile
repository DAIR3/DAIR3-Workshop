compile:
	g++ -o RawToCsv Source.cpp
compileStat:
	g++ -o Stat PointBiserial.cpp
compile2:
	g++ -o RawToCsv convertAll.cpp
run:
	qsub -q rcc-30d sub.sh
runStat:
	qsub -q rcc-30d subStat.sh
clean:
	rm RawToCsv
	rm sub.sh.*
cleanAll:
	rm termPregnancies*
	rm TestResults1988.csv	
	rm subStat.sh.*
	rm Stat
