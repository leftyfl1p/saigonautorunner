@interface SaigonViewController
-(UIButton *)jailbreakButton;
-(void)jailbreakReleased:(UIButton *)button;
//-(void)run;
//-(int)reinstallCydia;
@end


%group main

%hook SaigonViewController

-(void)viewDidLoad {
	%orig;
	//HBLogInfo(@"reinstallCydia: %d", [self reinstallCydia]);
	if([self jailbreakButton].isEnabled) {
		[NSTimer scheduledTimerWithTimeInterval:15
			target:[NSBlockOperation blockOperationWithBlock:^{
				[self jailbreakReleased:[self jailbreakButton]];
			}]
			selector:@selector(main)
			userInfo:nil
			repeats:NO
		];

	} else {
		HBLogError(@"com.leftyfl1p.saigonautorunner.trybuttondisabled");
	}

}

// -(int)reinstallCydia {
// 	return 1;
// }

%end

%hook AlertViewController

-(void)viewDidLoad {
	%orig;
	HBLogError(@"com.leftyfl1p.saigonautorunner.rebootrequested");

}

%end


%end



%ctor {

	%init(main);
	//%init(main,SaigonViewController=objc_getClass("Saigon.SaigonViewController"),AlertViewController=objc_getClass("Saigon.AlertViewController") );

}