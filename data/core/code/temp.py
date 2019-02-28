Rogue='''
     ARROW DAMAGE:  {dmg}
  SLOW DOWN ENEMY:  {slow}%
 DAMAGE OVER TIME:  {bleed}%
 PASS THRUE ENEMY:  {pierce}%
       DOUBLE HIT:  {barbs}%'''
Witch='''
 LIHGTNING DAMAGE
   -TO FAR TARGET:  {far_dmg}
  -TO NEAR TARGET:  {near_dmg}
MAGIC BOLT DAMAGE:  {dmg}
  BOLT BLAST SIZE:  {blast}'''
Gladiator='''
     SWORD DAMAGE:  {dmg}
     CRITICAL HIT:  {critical}%
       MOVE SPEED:  {speed}%
     BLOCK DAMAGE:  {block}%
     REGENERATION:  {regen}HP/S
       HIT POINTS:  {hp}'''
Druid='''
     MAGMA DAMAGE:  {magma_dmg}
  MAX MAGMA BLOBS:  {magma_num}
   MAGMA DURATION:  {magma_life}
       MAGMA SIZE:  {magma_size}
   TELEPORT SPEED:  {tele_speed}
TELEPORT COOLDOWN:  {tele_cool}
'''


tooltip_text=[None, 
           {"1A":"ARMOR:\nYou have more Hit Points\n",
           "1B":"REGENERATION:\nYou heal over time\n",
           "2A":"BLOCK:\nYour block is more effective\n",
           "2B":"SPEED:\nYour move faster\n",
           "3A":"DAMAGE:\nYou deal more damage\n",
           "3B":"CRITICAL HIT:\nChance for a critical hit\n"},
          {"1A":"BLAST:\nBigger Magic Bolt explosion\n",
           "1B":"DAMAGE:\nMagic Bolt deals more damage\n",
           "2A":"LIGHTNING:\nMore damage to far targets\n",
           "2B":"THUNDER:\nMore damage to near targets\n",
           "3A":"RAPID CHARGE:\nExponential damage increase\n",
           "3B":"STATIC CHARGE:\nLinear damage increase\n"},                           
          {"1A":"BARBS:\nOne hit counts as two\n",
           "1B":"PIERCE:\nArrows pass through targets\n",
           "2A":"BLEED:\nDamage over time\n",
           "2B":"CRIPPLE:\nSlow down enemies\n",
           "3A":"FINESSE:\nMore critical hits\n",
           "3B":"PROWESS:\nMore damage\n"},                           
          {"1A":"BURNING DEATH:\nMagma deals more damage\n",
           "1B":"MAGMA FLOW:\nMore magma at once\n",
           "2A":"HEART OF FIRE:\nMagma lasts longer\n",
           "2B":"VOLCANIC ACTIVITY:\nMagma is bigger\n",
           "3A":"PHASESHIFT:\nYou can teleport more often\n",
           "3B":"WARP FIELD:\nFaster recovery after teleport\n"} ]
if self.current_class=="2":    
            if option=="1A":
                return "{0}% blast size".format(value+50)
            elif option=="1B":
                return "{0}% damage".format(75+(101-value)/2)
            elif option=="2A":
                return "{0}% damage to far targets".format(value*2)
            elif option=="2B":
                return "{0}% damage to near targets\n".format(2*(100-value))
            elif option=="3A":
                return "{0}-{1} Lightning damage\n{2}-{3} Magic Bolt damage".format(
                                                                                    int(round(value/100.0+8*(101-value)/100.0)),
                                                                                    int(round(15*value/100.0+8*(101-value)/100)),
                                                                                    2*int(round(2*value/100.0+6*(101-value)/100.0)),
                                                                                    2*int(round(26*value/100.0+20*(101-value)/100))
                                                                                    )
            elif option=="3B":
                return "{0}-{1} Lightning damage\n{2}-{3} Magic Bolt damage".format(
                                                                                    int(round(value/100.0+8*(101-value)/100.0)),
                                                                                    int(round(15*value/100.0+8*(101-value)/100)),
                                                                                    2*int(round(2*value/100.0+6*(101-value)/100.0)),
                                                                                    2*int(round(26*value/100.0+20*(101-value)/100))
                                                                                    )
        elif self.current_class=="1":    
            if option=="1A":
                return "{0} total HP".format(value+50)
            elif option=="1B":
                return "+{0}HP/second".format(round((101-value)/100.0, 1))
            elif option=="2A":
                return "{0}% damage blocked".format(50+(value+1)/2)
            elif option=="2B":
                return "{0}% movement speed".format(75+(101-value)/2)
            elif option=="3A":
                return "{0}-{1} damage".format( int(round(1.0+(value+1.0)/100.0)), int(round(15.0*(1.0+(value+1.0)/50.0))))
            elif option=="3B":
                return "{0}% chance for +{1} damage".format(5+(101-value)/2,5+(101-value)/5)
                
        elif self.current_class=="3":    
            if option=="1A":
                return "{0}% chance to activate".format(int(value/2))
            elif option=="1B":
                return "{0}%chance to pierce".format(int((100-value)/2))
            elif option=="2A":
                return "{0}% of critical hits".format(int(value))
            elif option=="2B":
                return "{0}% of critical hits".format(int(100-value))
            elif option=="3A":
                return "{0}% chance for critical hit".format(25+ int(value/2))
            elif option=="3B":
                return "{0}% damage".format(50+int(100-value))   
        elif self.current_class=="4":    
            if option=="1A":
                return "{0}% damage".format(50+int(value))
            elif option=="1B":
                v=1+int((100-value)/20)
                if v<2:
                    return "Control 1 orb of magma"                    
                return "Control {0} orbs of magma".format(v)
            elif option=="2A":
                return "{0}% time".format(50+int(value))
            elif option=="2B":
                return "{0}% size".format(50+int(100-value))
            elif option=="3A":
                return "Teleport every {0} seconds".format(16.0*((100-value)/1000.0)+0.8)
            elif option=="3B":
                return "{0}% recovery time".format(50+int(value))
        