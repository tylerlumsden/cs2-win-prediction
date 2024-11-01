package main

import (
	"fmt"
	"log"
	"os"
	"time"
	"sort"
	//"encoding/json"

	dem "github.com/markus-wa/demoinfocs-golang/v4/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v4/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v4/pkg/demoinfocs/events"
	"github.com/gocarina/gocsv"
)

type FormattedTick struct {
	CT_X1 float64
	CT_X2 float64
	CT_X3 float64
	CT_X4 float64
	CT_X5 float64
	CT_Y1 float64
	CT_Y2 float64
	CT_Y3 float64
	CT_Y4 float64
	CT_Y5 float64

	T_X1 float64
	T_X2 float64
	T_X3 float64
	T_X4 float64
	T_X5 float64
	T_Y1 float64
	T_Y2 float64
	T_Y3 float64
	T_Y4 float64
	T_Y5 float64

	AliveCT_1 bool
	AliveCT_2 bool
	AliveCT_3 bool
	AliveCT_4 bool
	AliveCT_5 bool

	AliveT_1 bool
	AliveT_2 bool
	AliveT_3 bool
	AliveT_4 bool
	AliveT_5 bool

	Tick int
	Round int
	TimeLeft float64
	Winner int

}

type Tick struct {
	PlayerT []Player
	PlayerCT []Player
	Tick int
	Round int
	TimeLeft float64
	Winner int
}

type Player struct {
	X float64
	Y float64
	IsAlive bool
}

func main() {

	demoName := os.Args[1]
	fmt.Println(demoName)

	f, err := os.Open("demos/" + demoName)
	if err != nil {
		log.Panic("failed to open demo file: ", err)
	}
	defer f.Close()

	p := dem.NewParser(f)
	defer p.Close()

	fmt.Println("Parsing")
	start := time.Now()

	TickList := []Tick{}
	RoundWinner := map[int]int{}
	RoundStart := map[int]time.Duration{}

	roundLive := false
	BombIsPlanted := false
	freezeTime := false

	var PlantTime time.Duration

	p.RegisterEventHandler(func(e events.BombPlanted) {
		PlantTime = p.CurrentTime()
		BombIsPlanted = true
	})

	p.RegisterEventHandler(func(e events.RoundStart) {
		roundLive = true
		freezeTime = true
	})

	p.RegisterEventHandler(func (e events.RoundEnd) {

		roundLive = false
		BombIsPlanted = false

		if e.Winner == 2 {
			RoundWinner[p.GameState().TotalRoundsPlayed() - 1] = 0
		}
		if e.Winner == 3 {
			RoundWinner[p.GameState().TotalRoundsPlayed() - 1] = 1
		}
	})


	p.RegisterEventHandler(func(e events.RoundFreezetimeEnd) {
		freezeTime = false
		RoundStart[p.GameState().TotalRoundsPlayed()] = p.CurrentTime()
	})

	p.RegisterEventHandler(func (e events.FrameDone) {
		if p.GameState().IsMatchStarted() && roundLive {

			if !freezeTime {
				Tick := Tick{}
				for _, player := range p.GameState().Participants().Playing() {
					
					Player := Player{X: player.Position().X, Y: player.Position().Y, IsAlive: player.IsAlive()}

					if player.Team == common.TeamCounterTerrorists {
						Tick.PlayerCT = append(Tick.PlayerCT, Player)
					}
					if player.Team == common.TeamTerrorists {
						Tick.PlayerT = append(Tick.PlayerT, Player)
					}
				}

				sort.Slice(Tick.PlayerCT, func(i, j int) bool {
					return Tick.PlayerCT[i].X < Tick.PlayerCT[j].X
				})

				sort.Slice(Tick.PlayerT, func(i, j int) bool {
					return Tick.PlayerT[i].X < Tick.PlayerT[j].X
				})

				roundTime := time.Duration(115 * time.Second)
				plantDuration := time.Duration(40 * time.Second)

				if BombIsPlanted {
					timeLeft := (plantDuration) - (p.CurrentTime() - PlantTime)

					Tick.TimeLeft = timeLeft.Seconds()
				} else {
					timeLeft := (roundTime) - (p.CurrentTime() - RoundStart[p.GameState().TotalRoundsPlayed()])

					Tick.TimeLeft = timeLeft.Seconds()
				}
				Tick.Tick = p.GameState().IngameTick()
				Tick.Round = p.GameState().TotalRoundsPlayed()
				TickList = append(TickList, Tick)
			}
		}
	})



	err = p.ParseToEnd()
	if err != nil {
		log.Panic("failed to parse demo: ", err)
	}

	elapsed := time.Since(start)

	fmt.Printf("parse took %s\n", elapsed)

	for i := range TickList {
		TickList[i].Winner = RoundWinner[TickList[i].Round]
	}

	FormattedTickList := []FormattedTick{}
	for _, tick := range TickList {
		formattedtick := FormattedTick{}
		
		if len(tick.PlayerCT) >= 5 {
			formattedtick.CT_X1 = tick.PlayerCT[0].X
			formattedtick.CT_X2 = tick.PlayerCT[1].X
			formattedtick.CT_X3 = tick.PlayerCT[2].X
			formattedtick.CT_X4 = tick.PlayerCT[3].X
			formattedtick.CT_X5 = tick.PlayerCT[4].X

			formattedtick.CT_Y1 = tick.PlayerCT[0].Y
			formattedtick.CT_Y2 = tick.PlayerCT[1].Y
			formattedtick.CT_Y3 = tick.PlayerCT[2].Y
			formattedtick.CT_Y4 = tick.PlayerCT[3].Y
			formattedtick.CT_Y5 = tick.PlayerCT[4].Y

			formattedtick.AliveCT_1 = tick.PlayerCT[0].IsAlive
			formattedtick.AliveCT_2 = tick.PlayerCT[1].IsAlive
			formattedtick.AliveCT_3 = tick.PlayerCT[2].IsAlive
			formattedtick.AliveCT_4 = tick.PlayerCT[3].IsAlive
			formattedtick.AliveCT_5 = tick.PlayerCT[4].IsAlive
		}
		if len(tick.PlayerT) >= 5 {
			formattedtick.T_X1 = tick.PlayerT[0].X
			formattedtick.T_X2 = tick.PlayerT[1].X
			formattedtick.T_X3 = tick.PlayerT[2].X
			formattedtick.T_X4 = tick.PlayerT[3].X
			formattedtick.T_X5 = tick.PlayerT[4].X

			formattedtick.T_Y1 = tick.PlayerT[0].Y
			formattedtick.T_Y2 = tick.PlayerT[1].Y
			formattedtick.T_Y3 = tick.PlayerT[2].Y
			formattedtick.T_Y4 = tick.PlayerT[3].Y
			formattedtick.T_Y5 = tick.PlayerT[4].Y

			formattedtick.AliveT_1 = tick.PlayerT[0].IsAlive
			formattedtick.AliveT_2 = tick.PlayerT[1].IsAlive
			formattedtick.AliveT_3 = tick.PlayerT[2].IsAlive
			formattedtick.AliveT_4 = tick.PlayerT[3].IsAlive
			formattedtick.AliveT_5 = tick.PlayerT[4].IsAlive
		}

		formattedtick.Tick = tick.Tick
		formattedtick.Round = tick.Round
		formattedtick.Winner = tick.Winner
		formattedtick.TimeLeft = tick.TimeLeft

		FormattedTickList = append(FormattedTickList, formattedtick)
	}

	file, err := os.Create("csv/" + demoName + ".csv")
	if err != nil {
		log.Panic(err)
	}

	err = gocsv.MarshalFile(FormattedTickList, file) // Use this to save the CSV back to the file
	if err != nil {
		log.Panic(err)
	}
}