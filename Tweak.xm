@interface SaigonViewController
-(UIButton *)tryButton;
-(void)runbutton_hit:(UIButton *)button;
-(void)run;
-(int)reinstallCydia;
@end


%group main

%hook SaigonViewController

-(void)viewDidLoad {
	%orig;
	HBLogInfo(@"reinstallCydia: %d", [self reinstallCydia]);
	if([self tryButton].isEnabled) {
		[NSTimer scheduledTimerWithTimeInterval:15
			target:[NSBlockOperation blockOperationWithBlock:^{
				[self runbutton_hit:[self tryButton]];
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

	// sleep(30);
	// exit(0);
}

%end

// %hookf(int, printf, const char *format, ...) {
// 	//format = [NSString stringWithFormat:@"hooked %@", format];
// 	NSString *string = [NSString stringWithCString:format encoding:NSASCIIStringEncoding];
// 	//HBLogError(@"test: %@", string);
// 	%orig(##__VA_ARGS__);
// 	 // char formatted_string[MAX_FMT_SIZE];

// 	 // va_list argptr;
// 	 // va_start(argptr,format);
// 	 // format_string(format, argptr, formatted_string);
// 	 // va_end(argptr);
// 	 // fprintf(stdout, "%s",formatted_string);

// 	return 0;
// }

%end

//#define fNSLog(FORMAT, ...)
//int printf(const char *format, ...)
// int (*Origprintf)(const char *format, ...);
// //void OrigNSLog(NSString *format, ...);

// int Newprintf(const char *format, ...) {
// 	NSString *string = [NSString stringWithCString:format encoding:NSASCIIStringEncoding];
// 	if([string hasPrefix:@"[ERROR]: encoding frames for address"]) {
// 		string = [NSString stringWithFormat:@"USESPRINTF %@", string];
// 		HBLogDebug(@"%@", string);
// 	} else {
// 		return Origprintf(format);
// 	}
	
	
// 	return 0;

// 	//NSLog(@"[%@]: %@",@"Appendix" , [NSString stringWithFormat:format, ##__VA_ARGS__])
// }


// static void (*original_NSLog) (NSString *format, ...);

// void replaced_NSLog(NSString *format, ...) { original_NSLog(format, __VA_ARGS__); }


%ctor {
	%init(main,SaigonViewController=objc_getClass("Saigon.SiagonViewController"),AlertViewController=objc_getClass("Saigon.AlertViewController") );
	//MSHookFunction( (int *)printf, (void *)Newprintf, (void **)&Origprintf);
	//MSHookFunction(NSLog, replaced_NSLog, &original_NSLog);
}